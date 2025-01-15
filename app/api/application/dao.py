import asyncio
import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.application.redis_client import RedisClientApplication
from app.api.application.schemas import (
    ApplicationFilterSchema,
    ApplicationRespSchema,
    ApplicationSchema,
    ApplicationsPagFilterSchema,
    ApplicationUpdateResponseSchema,
    ApplicationUpdateSchema,
)
from app.api.application.utils import ActionType, create_message
from app.dao.base import BaseDAO
from app.kafka.producer import KafkaProducer
from app.models import Application

logger = logging.getLogger(__name__)


class ApplicationDAO(BaseDAO):
    application = Application
    model = application

    @classmethod
    async def create_an_application(
        cls,
        data: ApplicationSchema,
        session: AsyncSession,
        kafka: KafkaProducer,
    ) -> ApplicationRespSchema:
        try:
            result = await cls.add(session, data)

            application = ApplicationRespSchema.model_validate(result)

            message = create_message(
                action=ActionType.CREATE_APPLICATION,
                application_id=application.id,
                new_data=data.model_dump(),
            )
            await kafka.send_message(message=message)

            logger.info(f"Заявка {application} успешно создана")
            return application

            # пример без наследования
            # insert_applications = cls.model(**application_data.model_dump())
            # session.add(insert_applications)
            # await session.flush()
            # logger.info(f"Заявка {application} успешно создана")
            # return ApplicationRespSchema.model_validate(insert_applications)

        except IntegrityError:
            raise HTTPException(status_code=400, detail="User already exists")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при создании заявки {data} {e=!r}")
            raise HTTPException(status_code=500, detail="Ошибка базы данных")

    @classmethod
    async def get_application_by_id(
        cls,
        applications_id: int,
        session: AsyncSession,
        redis: RedisClientApplication,
    ) -> ApplicationRespSchema:
        cache = await redis.cached_application(applications_id)
        if cache:
            return ApplicationRespSchema(id=applications_id, **cache)

        result = await cls.find_one_or_none_by_id(data_id=applications_id, session=session)

        if not result:
            raise HTTPException(status_code=404, detail=f"Заявка {applications_id} не найдена")

        application = ApplicationRespSchema.model_validate(result)
        await redis.set_application_cache(applications_id, application.model_dump())

        return application

    @classmethod
    async def delete_application(
        cls,
        applications_id: int,
        session: AsyncSession,
        redis: RedisClientApplication,
        kafka: KafkaProducer,
    ):
        delete_application = ApplicationFilterSchema(id=applications_id)
        message = create_message(action=ActionType.DELETE_APPLICATION, application_id=applications_id)
        try:
            # todo: "параллельно"
            result, *_ = await asyncio.gather(
                cls.delete(session=session, filters=delete_application),
                redis.delete_application_cache(applications_id),
                kafka.send_message(message=message),
            )
            if not result:
                raise HTTPException(status_code=404, detail=f"Заявка {applications_id} не найдена")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении заявки {applications_id} {e=!r}")
            raise HTTPException(status_code=500, detail="Ошибка базы данных")
        # можно вернуть message
        # return ApplicationDeleteSchema(message=f"Заявка {applications_id} успешно удалена")

    @classmethod
    async def update_application(
        cls,
        applications_id: int,
        update_data: ApplicationUpdateSchema,
        session: AsyncSession,
        redis: RedisClientApplication,
        kafka: KafkaProducer,
    ) -> ApplicationUpdateResponseSchema:
        update_filter = ApplicationFilterSchema(id=applications_id)
        message = create_message(
            action=ActionType.UPDATE_APPLICATION,
            application_id=applications_id,
            update_data=update_data.model_dump(),
        )
        try:
            # todo: "параллельно"
            result, *_ = await asyncio.gather(
                cls.update(session, update_filter, update_data),
                redis.update_application_cache(applications_id, update_data.model_dump()),
                kafka.send_message(message=message),
            )

            if not result:
                raise HTTPException(status_code=404, detail=f"Заявка {applications_id} не найдена")
        # todo: по хорошему через авторизацию юзера или не менять user_name
        except IntegrityError:
            raise HTTPException(status_code=400, detail="User already exists")

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении заявки {applications_id} {e=!r}")
            raise HTTPException(status_code=500, detail="Ошибка базы данных")

        return ApplicationUpdateResponseSchema(message=f"Заявка {applications_id} успешно обновлена")

    @classmethod
    async def get_applications(
        cls,
        page: int,
        page_size: int,
        session: AsyncSession,
        user_name: str | None = None,
    ) -> list[ApplicationRespSchema]:
        filters = {}
        if user_name is not None:
            filters["user_name"] = user_name.lower()
        try:
            result = await cls.paginate(
                session=session,
                page=page,
                page_size=page_size,
                filters=ApplicationsPagFilterSchema(**filters),
            )
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении списка заявок {e=!r}")
            raise HTTPException(status_code=500, detail="Ошибка базы данных")
        if not result:
            raise HTTPException(status_code=404, detail="Заявки не найдены")

        return [ApplicationRespSchema.model_validate(item) for item in result]
