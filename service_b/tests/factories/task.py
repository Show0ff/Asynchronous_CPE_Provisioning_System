import datetime
from app.models import TaskRecord, ProvisionParameters, TaskStatus
from factories.base import BaseFactory
from service_b.tests.factories.fuzzyies import FuzzySerialID


class TaskFactory(BaseFactory):
    class Meta:
        model = TaskRecord
        collection = "tasks"

    equipment_id = FuzzySerialID()
    parameters = ProvisionParameters(
        username="admin",
        password="admin",
        interfaces=[1],
    )
    timestamp = datetime.datetime.utcnow()
    status = TaskStatus.running
