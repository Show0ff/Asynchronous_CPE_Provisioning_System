import pytest
from httpx import AsyncClient
from fastapi import status

from app.settings import task_repo
from factories.fuzzyies import FuzzySerialID
from tests.factories.task import ProvisionBodyFactory

BASE = "/api/v1/equipment/cpe"


@pytest.mark.asyncio
async def test_create_task_returns_200(async_client: AsyncClient):
    equipment_id = FuzzySerialID().fuzz()

    resp = await async_client.post(
        f"{BASE}/{equipment_id}",
        json=ProvisionBodyFactory.build_json(),
    )
    assert resp.status_code == status.HTTP_200_OK
    task_id = resp.json()["taskId"]

    rec = await task_repo.find_one({"id": task_id})
    assert rec and rec["status"] == "running"


@pytest.mark.asyncio
async def test_status_flow_running_then_completed(async_client: AsyncClient):
    equipment_id = FuzzySerialID().fuzz()
    resp = await async_client.post(
        f"{BASE}/{equipment_id}",
        json=ProvisionBodyFactory.build_json(),
    )
    task_id = resp.json()["taskId"]

    response_204 = await async_client.get(f"{BASE}/{equipment_id}/task/{task_id}")
    assert response_204.status_code == status.HTTP_204_NO_CONTENT

    await task_repo.update_one(
        {"id": task_id}, {"$set": {"status": "success", "outcome": "success"}}
    )

    response_200 = await async_client.get(f"{BASE}/{equipment_id}/task/{task_id}")
    assert response_200.status_code == status.HTTP_200_OK
    assert response_200.json()["message"] == "Completed"


@pytest.mark.asyncio
async def test_status_returns_500_on_failure(async_client: AsyncClient):
    equipment_id = FuzzySerialID().fuzz()
    resp = await async_client.post(
        f"{BASE}/{equipment_id}",
        json=ProvisionBodyFactory.build_json(),
    )
    task_id = resp.json()["taskId"]

    await task_repo.update_one(
        {"id": task_id}, {"$set": {"status": "failure", "outcome": "failure"}}
    )

    resp = await async_client.get(f"{BASE}/{equipment_id}/task/{task_id}")
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.json()["detail"] == "Internal provisioning exception"
