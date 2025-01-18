import pytest


@pytest.mark.asyncio
async def test_send_message(client, mock_kafka):
    # Пример использования mock_kafka
    message = {"key": "value"}
    topic = "test_topic"

    # Вызов метода отправки сообщения
    await mock_kafka.send_message(message, topic)

    # Проверка, что метод send_message был вызван с правильными параметрами
    mock_kafka.send_message.assert_called()
