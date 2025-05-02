import uvicorn
from fastapi import FastAPI

from app.routers import provision
from app.settings import settings


app = FastAPI()
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
