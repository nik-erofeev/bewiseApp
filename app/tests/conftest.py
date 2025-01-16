import json
import os
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import insert

from app.api.application.redis_client import RedisClientApplication
from app.core.settings import APP_CONFIG
from app.dao.database import async_session_maker, Base, engine
from app.main import app as fastapi_app
from app.models import Application

# @pytest.fixture
# def anyio_backend():
#     return "asyncio"


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    assert APP_CONFIG.environment == "test"

    # Создание и очистка базы данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        file_path = os.path.join(os.path.dirname(__file__), f"mock_{model}.json")
        with open(file_path, encoding="utf-8") as file:
            return json.load(file)

    # Загрузка тестовых данных
    applications = open_mock_json("applications")

    async with async_session_maker() as session:
        try:
            add_applications = insert(Application).values(applications)
            await session.execute(add_applications)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

    yield

    # Очистка базы данных после теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client():
    with TestClient(fastapi_app) as cli:
        return cli


# для lifespan через  AsyncClient
# @pytest.fixture(scope="session")
# async def _app():
#     # (создаем app) через импорт 'app' - todo: не пройдет lifespan
#     cong = AppConfig()
#     app = create_app(cong)
#     async with LifespanManager(app=app) as manager:
#         yield manager.app
#
# аналогично TestClient.  + добавить await (в тестах)
# @pytest_asyncio.fixture(scope="session")
# async def client(_app):
#     async with httpx.AsyncClient(app=_app, base_url="http://testclient") as client:
#         yield client


# возможно удалить(не рабочая)
@pytest.fixture
def kafka_producer_mock(mocker):
    # Мокируем Kafka продюсер
    return mocker.patch("app.kafka.producer.KafkaProducer")


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    client = RedisClientApplication(APP_CONFIG.redis)

    client.get_cache = AsyncMock()
    client.set_cache = AsyncMock()
    client.del_cache = AsyncMock()

    return client
