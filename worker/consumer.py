import asyncio
import json
import httpx
import aiormq
from aio_pika import connect_robust, Message, DeliveryMode

from settings import settings
from models import Task, Result

TASK_QUEUE = "config_tasks"
RESULT_QUEUE = "config_results"


async def wait_for_rabbitmq(url: str, timeout: int = 30):
    for i in range(timeout):
        try:
            conn = await connect_robust(url)
            await conn.close()
            return
        except aiormq.exceptions.AMQPConnectionError:
            await asyncio.sleep(1)
    raise RuntimeError("RabbitMQ is not reachable after 30 seconds")


async def run_worker():
    await wait_for_rabbitmq(str(settings.rabbit_url))

    conn = await connect_robust(str(settings.rabbit_url))
    chan = await conn.channel()
    queue = await chan.declare_queue(TASK_QUEUE, durable=True)

    async with queue.iterator() as it:
        async for msg in it:
            async with msg.process():
                body = json.loads(msg.body)
                task = Task(**body)

                base = str(settings.service_a_url).rstrip("/")

                try:
                    async with httpx.AsyncClient(
                        timeout=task.timeoutInSeconds
                    ) as client:
                        r = await client.post(
                            f"{base}/api/v1/equipment/cpe/{task.equipmentId}",
                            json={
                                "timeoutInSeconds": task.timeoutInSeconds,
                                "parameters": task.parameters,
                            },
                        )
                    outcome = "success" if r.status_code == 200 else "failure"
                except Exception:
                    outcome = "failure"

                result = Result(taskId=task.taskId, outcome=outcome)
                await chan.default_exchange.publish(
                    Message(
                        result.model_dump_json().encode(),
                        delivery_mode=DeliveryMode.PERSISTENT,
                    ),
                    routing_key=RESULT_QUEUE,
                )
