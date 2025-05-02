from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    rabbit_url: AnyUrl
    service_a_url: AnyUrl

    model_config = {"env_file": ".env"}


settings = Settings()
