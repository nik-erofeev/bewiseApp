import json
import logging

from aiokafka import AIOKafkaProducer

from app.core.settings import APP_CONFIG

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self, bootstrap_servers: str, topik: str):
        self.bootstrap_servers = bootstrap_servers
        self.default_topic = topik
        self.producer = None

    async def start(self):
        try:
            self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await self.producer.start()
            logger.debug(f"Kafka producer connected to {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Kafka producer: {e}")
            raise

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            self.producer = None
            logger.debug("Kafka producer disconnected")

    async def get_producer(self) -> AIOKafkaProducer:
        if self.producer is None:
            raise RuntimeError("Producer is not started")
        return self.producer

    async def send_message(self, message: dict, topic: str | None = None):
        if topic is None:
            topic = self.default_topic
        message_bytes = json.dumps(message).encode("utf-8")

        if self.producer is None:
            raise RuntimeError("Producer is not started. Please call start() before sending messages.")

        try:
            logger.info(f"Sending Kafka message {message} to topic {topic}")
            await self.producer.send_and_wait(topic, value=message_bytes)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в Kafka: {e}")
            raise


kafka_producer = KafkaProducer(
    APP_CONFIG.kafka.bootstrap_servers,
    APP_CONFIG.kafka.topik,
)
