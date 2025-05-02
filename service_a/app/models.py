from pydantic import BaseModel, Field, constr

from app.constants import SERIAL_ID_REGEX

SerialID = constr(pattern=SERIAL_ID_REGEX)


class ProvisionParameters(BaseModel):
    username: str
    password: str
    vlan: int | None = None
    interfaces: list[int]


class ProvisionRequest(BaseModel):
    timeoutInSeconds: int = Field(gt=0)
    parameters: ProvisionParameters


class APIResponse(BaseModel):
    code: int
    message: str
