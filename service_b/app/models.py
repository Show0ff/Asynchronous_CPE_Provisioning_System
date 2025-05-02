from enum import StrEnum
from datetime import datetime
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


class APIProvisionResponse(BaseModel):
    code: int
    taskId: str


class APIStatusResponse(BaseModel):
    code: int
    message: str


class TaskStatus(StrEnum):
    running = "running"
    success = "success"
    failure = "failure"


class TaskRecord(BaseModel):
    id: str
    equipment_id: str
    parameters: ProvisionParameters
    timestamp: datetime
    status: TaskStatus = TaskStatus.running
