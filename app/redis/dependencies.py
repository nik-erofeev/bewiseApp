import logging
from collections.abc import AsyncGenerator

from fastapi import Depends

from app.api.application.redis_client import redis_cli, RedisClientApplication

logger = logging.getLogger(__name__)


# если хотим каждый раз получать новый коннект к Redis (а не держать постоянный)! :todo: +убрать из lifespan redis_cli.setup() / redis_cli.close()
async def get_redis_client() -> AsyncGenerator[RedisClientApplication, None]:
    await redis_cli.setup()
    try:
        logger.debug("Starting Redis client...")
        yield redis_cli
        logger.debug("Closing Redis client...")
    finally:
        await redis_cli.close()


RedisClientApplicationDep = Depends(get_redis_client)


# если хотим  держать постоянный коннект! :todo: +  lifespan redis_cli.setup() / redis_cli.close()
# class RedisClientApplicationManager:
#     """
#     Класс для управления клиентом Redis для тарифов.
#     """
#
#     def __init__(self, redis_client: RedisClientApplication):
#         self.redis_client = redis_client
#
#     async def get_client(self) -> RedisClientApplication:
#         """
#         Зависимость для FastAPI, возвращающая экземпляр клиента RedisTariff.
#         """
#         return self.redis_client


# redis_manager = RedisClientApplicationManager(redis_cli)
# RedisClientApplicationDep = Depends(redis_manager.get_client)
