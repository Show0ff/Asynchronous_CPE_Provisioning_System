from factory import Factory, base, enums
from motor.motor_asyncio import AsyncIOMotorClient
from tests.conftest import DB_NAME


class MongoOptions(base.FactoryOptions):
    def _build_default_options(self):
        return super()._build_default_options() + [
            base.OptionDefault("collection", None, inherit=True),
            base.OptionDefault("data_layer", DB_NAME, inherit=True),
        ]


class AsyncMongoFactory(Factory):
    _options_class = MongoOptions
    _original_params = None

    class Meta:
        abstract = True
        strategy = enums.CREATE_STRATEGY

    @classmethod
    def _generate(cls, strategy, params):
        cls._original_params = params
        return super()._generate(strategy, params)

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        return model_class(*args, **kwargs)

    @classmethod
    def __get_database(cls):
        client = AsyncIOMotorClient(db.get_url())
        return client[cls._meta.data_layer]

    @classmethod
    async def _create(cls, model_class, **kwargs):
        instance = model_class(**kwargs)
        data = instance.dict()
        database = cls.__get_database()
        result = await database[cls._meta.collection].insert_one(data)
        return model_class(**kwargs, _id=result.inserted_id)

    @classmethod
    async def create(cls, **kwargs):
        instance_built = cls.build(**kwargs)
        return await cls._create(cls._meta.model, **instance_built.dict())

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]
