import logging

from app.redis.redis_client import ExpireTime, RedisClient, RedisKeys

logger = logging.getLogger(__name__)


class RedisClientApplication(RedisClient):
    async def cached_application(self, application_id: int) -> dict | None:
        try:
            cache = await self.get_cache(RedisKeys.APPLICATION, str(application_id))
            if cache is None:
                logger.debug("Кэш заявок пуст.")
                return None
            return cache
        except Exception as e:
            logger.error(f"Ошибка при получении кэша заявок: {e}")
            return None

    async def set_application_cache(self, application_id: int, application_data: dict):
        try:
            application_data.pop("id", None)

            await self.set_cache(
                RedisKeys.APPLICATION,
                str(application_id),
                application_data,
                expire=ExpireTime.DAY.value,
            )

        except Exception as e:
            logger.error(f"Ошибка при сохранении заявки с ID {application_id}: {e}")

    async def update_application_cache(self, application_id: int, new_application_data: dict) -> None:
        try:
            existing_data = await self.get_cache(RedisKeys.APPLICATION, str(application_id))

            if existing_data:
                existing_data.update(new_application_data)
                await self.set_cache(
                    RedisKeys.APPLICATION,
                    str(application_id),
                    existing_data,
                    expire=None,
                )

        except Exception as e:
            logger.error(f"Ошибка при обновлении заявки с ID {application_id}: {e}")

    async def delete_application_cache(self, application_id: int) -> None:
        try:
            await self.del_cache(RedisKeys.APPLICATION, str(application_id))

        except Exception as e:
            logger.error(f"Ошибка при удалении заявки с ID {application_id}: {e}")
