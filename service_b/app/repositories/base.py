from abc import ABC
from motor.core import AgnosticCollection
from pydantic import BaseModel
from typing import Any, Generic, TypeVar

T = TypeVar("T", bound=BaseModel)


class MongoRepository(ABC, Generic[T]):
    data_type: type[T]

    def __init__(self, collection: AgnosticCollection):
        self._col = collection

    async def insert(self, obj: T) -> None:
        await self._col.insert_one(obj.model_dump())

    async def update_fields(self, obj_id: str, **fields) -> None:
        await self._col.update_one({"id": obj_id}, {"$set": fields})

    async def get(self, obj_id: str) -> T | None:
        doc = await self._col.find_one({"id": obj_id})
        return self.data_type(**doc) if doc else None

    async def find_one(self, filter: dict[str, Any]) -> dict | None:
        return await self._col.find_one(filter)

    async def update_one(self, filter: dict[str, Any], update: dict[str, Any]) -> None:
        await self._col.update_one(filter, update)
