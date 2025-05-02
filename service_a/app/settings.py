from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str
    port: int
    use_https: bool
    ssl_certfile: str | None = None
    ssl_keyfile: str | None = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
