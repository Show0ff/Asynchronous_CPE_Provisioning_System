from fastapi import HTTPException, APIRouter, Path, status, Depends, Body, Response
from aio_pika import Channel

from app.models import (
    ProvisionRequest,
    APIProvisionResponse,
    APIStatusResponse,
    TaskStatus,
)
from app.utils import get_rabbit_channel
from app.services import create_task, get_status
from app.constants import SERIAL_ID_REGEX

router = APIRouter(prefix="/api/v1/equipment")


@router.post("/cpe/{id}", response_model=APIProvisionResponse)
async def create_task_ep(
    id: str = Path(pattern=SERIAL_ID_REGEX),
    body: ProvisionRequest = Body(...),
    channel: Channel = Depends(get_rabbit_channel),
):
    task_id = await create_task(id, body, channel)
    return APIProvisionResponse(
        code=status.HTTP_200_OK,
        taskId=task_id,
    )


@router.get(
    "/cpe/{id}/task/{task}",
    response_model=APIStatusResponse,
)
async def task_status_ep(
    id: str = Path(pattern=SERIAL_ID_REGEX),
    task: str = Path(),
):
    task_state = await get_status(id, task)

    if task_state == TaskStatus.running:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if task_state == TaskStatus.success:
        return APIStatusResponse(
            code=status.HTTP_200_OK,
            message="Completed",
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal provisioning exception",
    )
