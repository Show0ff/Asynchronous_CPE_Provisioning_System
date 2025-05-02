import uuid
import datetime
import json
from aio_pika import Channel, Message, DeliveryMode
from fastapi import HTTPException, status

from app.models import ProvisionRequest, TaskRecord, TaskStatus
from app.settings import task_repo
from app.constants import TASK_QUEUE


async def create_task(
    equipment_id: str,
    req: ProvisionRequest,
    channel: Channel,
) -> str:
    task_id = str(uuid.uuid4())
    task = TaskRecord(
        id=task_id,
        equipment_id=equipment_id,
        parameters=req.parameters,
        timestamp=datetime.datetime.utcnow(),
    )
    await task_repo.insert(task)

    payload = {
        "taskId": task_id,
        "equipmentId": equipment_id,
        "timeoutInSeconds": req.timeoutInSeconds,
        "parameters": req.parameters.model_dump(),
    }
    await channel.default_exchange.publish(
        Message(
            json.dumps(payload).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        ),
        routing_key=TASK_QUEUE,
    )
    return task_id


async def get_status(equipment_id: str, task_id: str) -> TaskStatus:
    rec = await task_repo.get(task_id)
    if not rec or rec.equipment_id != equipment_id:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "The requested task is not found"
        )
    return rec.status


async def save_result(task_id: str, outcome: str) -> None:
    await task_repo.set_status(
        task_id, TaskStatus.success if outcome == "success" else TaskStatus.failure
    )
