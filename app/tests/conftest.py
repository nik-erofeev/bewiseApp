import json
import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.core.settings import APP_CONFIG
from app.dao.database import async_session_maker, Base, engine
from app.main import app as fastapi_app
from app.models import Application


# без нее error бывает в async тестах
@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://testserver") as ac:
        yield ac


@pytest.fixture(autouse=True)
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


@pytest.fixture
def kafka_producer_mock(mocker):
    # Мокируем Kafka продюсер
    return mocker.patch("app.kafka.producer.KafkaProducer")


@pytest.fixture
def redis_client_mock(mocker):
    # Мокируем Redis клиент
    return mocker.patch("app.api.application.redis_client.RedisClientApplication")
