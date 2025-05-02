from app.repositories.base import MongoRepository
from app.models import TaskRecord, TaskStatus


class TaskRepository(MongoRepository[TaskRecord]):
    data_type = TaskRecord

    async def set_status(self, task_id: str, status: TaskStatus) -> None:
        await self.update_fields(task_id, status=status)
