from unittest.mock import AsyncMock

import pytest

from app.kafka.producer import KafkaProducer


@pytest.fixture
def kafka_producer():
    # producer = KafkaProducer(bootstrap_servers="localhost:29092", default_topic="test_topic")
    producer = KafkaProducer(bootstrap_servers="test:123", default_topic="test_topic")
    producer.producer = AsyncMock()  # Мокируем AIOKafkaProducer
    producer.admin_client = AsyncMock()  # Мокируем AIOKafkaAdminClient
    producer.admin_client.start = AsyncMock()  # Мокируем метод start
    return producer


# @pytest.mark.asyncio
# async def test_start_creates_topic(kafka_producer):
#     # Настраиваем поведение мока
#     kafka_producer.admin_client.list_topics = AsyncMock(return_value=[])
#     kafka_producer.admin_client.create_topics = AsyncMock()  # Мокируем метод create_topics
#
#     await kafka_producer.start()
#
#     # Проверяем, что тема была создана
#     kafka_producer.admin_client.create_topics.assert_called_once()
#     assert kafka_producer.producer is not None
#
#
# @pytest.mark.asyncio
# async def test_start_topic_exists(kafka_producer):
#     # Настраиваем поведение мока
#     kafka_producer.admin_client.list_topics = AsyncMock(return_value=["test_topic"])
#
#     await kafka_producer.start()
#
#     # Проверяем, что создание темы не было вызвано
#     kafka_producer.admin_client.create_topics.assert_not_called()
#     assert kafka_producer.producer is not None


async def test_stop_sends_remaining_batches(kafka_producer):
    # Настраиваем поведение мока
    kafka_producer.batches = {"test_topic": [b"message1", b"message2"]}
    kafka_producer.producer.send_and_wait = AsyncMock()

    await kafka_producer.stop()

    # Проверяем, что оставшиеся сообщения были отправлены
    kafka_producer.producer.send_and_wait.assert_called()
    assert kafka_producer.batches["test_topic"] == []  # Проверяем, что батчи очищены


async def test_send_message(kafka_producer):
    message = {"key": "value"}

    await kafka_producer.send_message(message)

    # Проверяем, что сообщение добавлено в батч
    assert len(kafka_producer.batches["test_topic"]) == 1
    assert kafka_producer.batches["test_topic"][0] == b'{"key": "value"}'


async def test_send_message_batch(kafka_producer):
    kafka_producer.batch_size = 2  # Устанавливаем размер батча для теста
    message1 = {"key": "value1"}
    message2 = {"key": "value2"}

    await kafka_producer.send_message(message1)
    await kafka_producer.send_message(message2)

    # Проверяем, что сообщения были отправлены в батче
    await kafka_producer.send_batch("test_topic")

    assert kafka_producer.producer.send_and_wait.call_count == 2
    kafka_producer.producer.send_and_wait.assert_any_call("test_topic", b'{"key": "value1"}')
    kafka_producer.producer.send_and_wait.assert_any_call("test_topic", b'{"key": "value2"}')
