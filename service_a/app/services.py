import asyncio
from fastapi import status

from app.models import ProvisionRequest, APIResponse


async def provision_device(_: str, __: ProvisionRequest) -> APIResponse:
    await asyncio.sleep(60)
    return APIResponse(code=status.HTTP_200_OK, message="success")
