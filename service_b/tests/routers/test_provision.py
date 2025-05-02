import pytest
from httpx import AsyncClient
from fastapi import status

from app.settings import task_repo
from tests.factories.fuzzyies import FuzzySerialID, FuzzyCred

BASE = "/api/v1/equipment/cpe"


@pytest.mark.asyncio
async def test_create_task_returns_200(async_client: AsyncClient):
    equipment_id = FuzzySerialID().fuzz()
    body = {
        "timeoutInSeconds": 70,
        "parameters": {
            "username": FuzzyCred().fuzz(),
            "password": FuzzyCred().fuzz(),
            "interfaces": [1],
        },
    }

    response = await async_client.post(f"{BASE}/{equipment_id}", json=body)
    assert response.status_code == status.HTTP_200_OK
    task_id = response.json()["taskId"]

    rec = await task_repo.find_one({"id": task_id})
    assert rec is not None
    assert rec["status"] == "running"


@pytest.mark.asyncio
async def test_status_flow_running_then_completed(
    async_client: AsyncClient,
):
    equipment_id = FuzzySerialID().fuzz()

    post = await async_client.post(
        f"{BASE}/{equipment_id}",
        json={
            "timeoutInSeconds": 70,
            "parameters": {"username": "admin", "password": "admin", "interfaces": [1]},
        },
    )
    task_id = post.json()["taskId"]

    response = await async_client.get(f"{BASE}/{equipment_id}/task/{task_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await task_repo.update_one(
        {"id": task_id}, {"$set": {"status": "success", "outcome": "success"}}
    )

    r2 = await async_client.get(f"{BASE}/{equipment_id}/task/{task_id}")
    assert r2.status_code == status.HTTP_200_OK
    assert r2.json()["message"] == "Completed"


@pytest.mark.asyncio
async def test_status_returns_500_on_failure(async_client: AsyncClient):
    equipment_id = FuzzySerialID().fuzz()

    post = await async_client.post(
        f"{BASE}/{equipment_id}",
        json={
            "timeoutInSeconds": 20,
            "parameters": {"username": "admin", "password": "admin", "interfaces": [1]},
        },
    )
    task_id = post.json()["taskId"]

    await task_repo.update_one(
        {"id": task_id}, {"$set": {"status": "failure", "outcome": "failure"}}
    )

    response = await async_client.get(f"{BASE}/{equipment_id}/task/{task_id}")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Internal provisioning exception"
