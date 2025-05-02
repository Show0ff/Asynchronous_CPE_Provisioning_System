import logging
from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from motor.motor_asyncio import AsyncIOMotorClient

from app.repositories.task import TaskRepository


class Settings(BaseSettings):
    app_mode: str = "prod"
    host: str
    port: int
    rabbit_url: AnyUrl
    service_a_url: AnyUrl
    mongo_url: str
    use_https: bool
    ssl_certfile: str | None = None
    ssl_keyfile: str | None = None

    model_config = {"env_file": ".env"}


settings = Settings()

mongo_client = AsyncIOMotorClient(settings.mongo_url)
mongo_db = mongo_client["tasks_db"]

task_repo = TaskRepository(collection=mongo_db["tasks"])


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
