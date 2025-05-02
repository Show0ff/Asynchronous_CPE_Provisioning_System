import random
from factory import Factory, LazyAttribute

from app.models import ProvisionRequest, ProvisionParameters
from tests.factories.fuzzyies import FuzzyCred


class ProvisionBodyFactory(Factory):
    """
    Генерирует dict для POST /cpe/{id}.
    """

    class Meta:
        model = ProvisionRequest

    timeoutInSeconds = LazyAttribute(lambda _: random.randint(61, 120))
    parameters = LazyAttribute(
        lambda _: ProvisionParameters(
            username=FuzzyCred().fuzz(),
            password=FuzzyCred().fuzz(),
            interfaces=[1],
        )
    )

    @classmethod
    def build_json(cls) -> dict:
        return cls.build().model_dump()
