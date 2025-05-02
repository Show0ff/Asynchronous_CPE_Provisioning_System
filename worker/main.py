import asyncio

from settings import settings
from consumer import run_worker, wait_for_rabbitmq


async def main():
    await wait_for_rabbitmq(str(settings.rabbit_url))
    await run_worker()


if __name__ == "__main__":
    asyncio.run(main())
