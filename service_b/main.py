import json
import asyncio
import contextlib
import logging
import uvicorn
import aiormq
from aio_pika import connect_robust
from fastapi import FastAPI

from app.constants import RESULT_QUEUE
from app.routers import provision
from app.settings import settings
from app.services import save_result


logger = logging.getLogger(__name__)


async def wait_for_rabbitmq(
    url: str,
    retries: int = 30,
    delay: int = 1,
):
    for attempt in range(retries):
        try:
            conn = await connect_robust(url)
            await conn.close()
            logger.info(f"RabbitMQ is ready (attempt {attempt + 1})")
            return
        except aiormq.exceptions.AMQPConnectionError:
            logger.warning(f"RabbitMQ not ready (attempt {attempt + 1})")
            await asyncio.sleep(delay)
    raise RuntimeError("RabbitMQ is not reachable after retrying")


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await wait_for_rabbitmq(str(settings.rabbit_url))
    conn = await connect_robust(str(settings.rabbit_url))
    chan = await conn.channel()
    queue = await chan.declare_queue(RESULT_QUEUE, durable=True)

    async def consume():
        async with queue.iterator() as it:
            async for msg in it:
                async with msg.process():
                    try:
                        body = json.loads(msg.body)
                        await save_result(
                            body.get("taskId", ""),
                            body.get("outcome", "failure"),
                        )
                    except Exception as e:
                        logger.exception(f"Failed to process message: {e}")

    task = asyncio.create_task(consume())

    yield

    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task
    await conn.close()


app = FastAPI(lifespan=lifespan)
app.include_router(provision.router)

if __name__ == "__main__":
    ssl = (
        {
            "ssl_certfile": settings.ssl_certfile,
            "ssl_keyfile": settings.ssl_keyfile,
        }
        if settings.use_https
        else {}
    )

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        **ssl,
    )
