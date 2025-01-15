from fastapi import APIRouter, Body, Query, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.application.dao import ApplicationDAO
from app.api.application.redis_client import RedisClientApplication
from app.api.application.schemas import (
    ApplicationCreateSchema,
    ApplicationRespSchema,
    ApplicationUpdateResponseSchema,
    ApplicationUpdateSchema,
)
from app.api.application.utils import description
from app.dao.session_maker import TransactionSessionDep
from app.kafka.dependencies import KafkaProducerDep
from app.kafka.producer import KafkaProducer
from app.redis.dependencies import RedisClientApplicationDep

router = APIRouter(
    prefix="/applications",
    tags=["Заявки"],
)


@router.post(
    "/",
    summary="Добавить заявку",
    response_model=ApplicationRespSchema,
    response_class=ORJSONResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_application(
    data: ApplicationCreateSchema = Body(example=description),
    session: AsyncSession = TransactionSessionDep,
    kafka: KafkaProducer = KafkaProducerDep,
):
    return await ApplicationDAO.create_an_application(data, session, kafka)


@router.get(
    "/{application_id}",
    summary="Получить заявку",
    response_model=ApplicationRespSchema,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def get_application(
    application_id: int,
    session: AsyncSession = TransactionSessionDep,
    redis: RedisClientApplication = RedisClientApplicationDep,
):
    return await ApplicationDAO.get_application_by_id(application_id, session, redis)


@router.get(
    "/",
    summary="Получить список заявок",
    response_model=list[ApplicationRespSchema],
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_applications(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Записей на странице"),
    user: str | None = None,
    session: AsyncSession = TransactionSessionDep,
):
    return await ApplicationDAO.get_applications(
        page,
        page_size,
        session,
        user,
    )


@router.delete(
    "/{application_id}",
    summary="Удалить заявку",
    status_code=status.HTTP_204_NO_CONTENT,
    # можно вернуть message
    # response_model=ApplicationDeleteSchema,
    # response_class=ORJSONResponse,
    # status_code=status.HTTP_200_OK,
)
async def delete_application(
    application_id: int,
    session: AsyncSession = TransactionSessionDep,
    redis: RedisClientApplication = RedisClientApplicationDep,
    kafka: KafkaProducer = KafkaProducerDep,
):
    return await ApplicationDAO.delete_application(
        application_id,
        session,
        redis,
        kafka,
    )


@router.patch(
    "/{application_id}",
    summary="Обновить заявку",
    response_model=ApplicationUpdateResponseSchema,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def update_application(
    application_id: int,
    new_application: ApplicationUpdateSchema = Body(example=description),
    session: AsyncSession = TransactionSessionDep,
    redis: RedisClientApplication = RedisClientApplicationDep,
    kafka: KafkaProducer = KafkaProducerDep,
):
    return await ApplicationDAO.update_application(
        application_id,
        new_application,
        session,
        redis,
        kafka,
    )
