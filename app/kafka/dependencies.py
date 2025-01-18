import logging
from collections.abc import AsyncGenerator

from fastapi import Depends

from app.kafka.producer import kafka_producer, KafkaProducer

logger = logging.getLogger(__name__)


# если хотим каждый раз получать новый коннект к Kafka (а не держать постоянный)
async def get_kafka_producer() -> AsyncGenerator[KafkaProducer, None]:
    await kafka_producer.start()
    try:
        logger.debug("Starting Kafka producer...")
        yield kafka_producer
        logger.debug("Stopping Kafka producer...")
    finally:
        await kafka_producer.stop()


KafkaProducerDep = Depends(get_kafka_producer)


# если нужен постоянный коннект к Kafka. + lifespan kafka_producer.start() / kafka_producer.stop()
# class KafkaProducerManager:
#     """
#     Класс для управления асинхронным продюсером Kafka.
#     """
#
#     def __init__(self, producer: KafkaProducer):
#         self.producer = producer
#
#     async def get_producer(self) -> KafkaProducer:
#         """
#         Зависимость для FastAPI, возвращающая экземпляр продюсера Kafka.
#         """
#         return self.producer


# kafka_producer_manager = KafkaProducerManager(kafka_producer)
# KafkaProducerDep = Depends(kafka_producer_manager.get_producer)
