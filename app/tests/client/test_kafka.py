import json
from unittest.mock import AsyncMock, patch

import pytest

from app.core.settings import APP_CONFIG
from app.kafka.producer import KafkaProducer


@pytest.fixture
async def kafka_producer():
    producer = KafkaProducer(bootstrap_servers=APP_CONFIG.kafka.bootstrap_servers, topik=APP_CONFIG.kafka.topik)
    await producer.start()
    yield producer
    await producer.stop()


@pytest.mark.asyncio
async def test_start(kafka_producer):
    assert kafka_producer.producer is not None


@pytest.mark.asyncio
async def test_stop(kafka_producer):
    await kafka_producer.stop()
    assert kafka_producer.producer is None


@pytest.mark.asyncio
async def test_send_message(kafka_producer):
    message = {"key": "value"}
    topic = "test_topic"

    with patch.object(kafka_producer.producer, "send_and_wait", new_callable=AsyncMock) as mock_send:
        await kafka_producer.send_message(message, topic)
        mock_send.assert_called_once_with(topic, value=json.dumps(message).encode("utf-8"))


@pytest.mark.asyncio
async def test_send_message_default_topic(kafka_producer):
    message = {"key": "value"}

    with patch.object(kafka_producer.producer, "send_and_wait", new_callable=AsyncMock) as mock_send:
        await kafka_producer.send_message(message)
        mock_send.assert_called_once_with(kafka_producer.default_topic, value=json.dumps(message).encode("utf-8"))


@pytest.mark.asyncio
async def test_get_producer(kafka_producer):
    producer = await kafka_producer.get_producer()
    assert producer is not None


@pytest.mark.asyncio
async def test_get_producer_not_started():
    producer = KafkaProducer(bootstrap_servers="error:9011192", topik="test_topic")
    with pytest.raises(RuntimeError, match="Producer is not started"):
        await producer.get_producer()
