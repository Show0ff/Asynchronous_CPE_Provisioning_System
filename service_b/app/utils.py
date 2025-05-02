from aio_pika import connect_robust, Channel

from app.settings import settings


async def get_rabbit_channel() -> Channel:
    return await (await connect_robust(str(settings.rabbit_url))).channel()
