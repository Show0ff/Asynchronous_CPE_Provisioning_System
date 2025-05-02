import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app as fastapi_app
from app.utils import get_rabbit_channel
from app.settings import mongo_client

DB_NAME = "tasks_db"


class DummyChannel:
    @property
    def default_exchange(self):
        return self

    async def publish(self, *args, **kwargs):
        return


@pytest.fixture(autouse=True)
def override_rabbit():
    fastapi_app.dependency_overrides[get_rabbit_channel] = lambda: DummyChannel()
    yield
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    db = mongo_client[DB_NAME]
    await db.drop_collection("tasks")
    yield
    await db.drop_collection("tasks")


@pytest_asyncio.fixture
async def async_client():

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
