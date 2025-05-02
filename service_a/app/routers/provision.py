from fastapi import APIRouter, Path, Body, status

from app.models import ProvisionRequest, APIResponse
from app.services import provision_device
from app.constants import SERIAL_ID_REGEX

router = APIRouter(prefix="/api/v1/equipment")


@router.post(
    "/cpe/{id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def provision_endpoint(
    id: str = Path(pattern=SERIAL_ID_REGEX),
    body: ProvisionRequest = Body(...),
) -> APIResponse:
    return await provision_device(id, body)
