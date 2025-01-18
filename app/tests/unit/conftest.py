from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.application.redis_client import RedisClientApplication
from app.application import create_app
from app.core.settings import AppConfig
from app.dao.session_maker import session_manager
from app.kafka.dependencies import get_kafka_producer
from app.kafka.producer import KafkaProducer
from app.redis.dependencies import get_redis_client

# Мок для KafkaProducer
mock_kafka_producer = AsyncMock(autospec=KafkaProducer)


async def mock_get_kafka_producer():
    await mock_kafka_producer.start()
    try:
        yield mock_kafka_producer
    finally:
        await mock_kafka_producer.stop()


# async def mock_get_kafka_producer():
#     yield mock_kafka_producer


@pytest.fixture
def mock_kafka():  # хз почему но обычные моки не АСИНХР
    return mock_kafka_producer


# мок редис клиента
mock_redis_client = AsyncMock(autospec=RedisClientApplication)


async def mock_get_redis_client():
    await mock_redis_client.setup()
    try:
        yield mock_redis_client
    finally:
        await mock_redis_client.close()


@pytest.fixture
def mock_redis():  # хз почему но обычные моки не АСИНХР
    return mock_redis_client


mock_session = AsyncMock(autospec=AsyncSession)


async def mock_get_session():
    # Мок для получения сессии без транзакции
    try:
        yield mock_session
        await mock_session.commit()
    finally:
        await mock_session.close()


async def mock_get_transaction_session():
    # Мок для получения сессии с управлением транзакцией
    try:
        yield mock_session
        await mock_session.commit()
    finally:
        await mock_session.close()


@pytest.fixture
def mock_db_session():  # хз почему но обычные моки не АСИНХР
    return mock_session


@pytest_asyncio.fixture
async def _app():
    config = AppConfig()
    app = create_app(config)

    # Переопределяем Depends[SessionDep]
    app.dependency_overrides[session_manager.get_session] = mock_get_session

    # Переопределяем Depends[TransactionSessionDep]
    app.dependency_overrides[session_manager.get_transaction_session] = mock_get_transaction_session

    # Переопределяем Depends[KafkaProducerDep]
    app.dependency_overrides[get_kafka_producer] = mock_get_kafka_producer

    # Переопределяем Depends[RedisClientApplicationDep]
    app.dependency_overrides[get_redis_client] = mock_get_redis_client

    return app


# todo: lifespan + transport=ASGITransport (на новых версиях)
@pytest_asyncio.fixture
async def client(_app):
    lifespan = LifespanManager(_app)
    httpx_client = AsyncClient(transport=ASGITransport(app=_app), base_url="http://testserver")
    async with httpx_client as client, lifespan:
        yield client
