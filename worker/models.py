from pydantic import BaseModel, PositiveInt, constr
from constants import SERIAL_ID_REGEX


SerialID = constr(pattern=SERIAL_ID_REGEX)


class Task(BaseModel):
    taskId: str
    equipmentId: SerialID
    timeoutInSeconds: PositiveInt
    parameters: dict


class Result(BaseModel):
    taskId: str
    outcome: str
