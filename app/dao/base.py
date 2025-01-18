import logging
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete as sqlalchemy_delete, update as sqlalchemy_update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .database import Base

# Объявляем типовой параметр T с ограничением, что это наследник Base
T = TypeVar("T", bound=Base)


logger = logging.getLogger(__name__)


class BaseDAO(Generic[T]):
    model: type[T]

    @classmethod
    async def find_one_or_none_by_id(
        cls,
        data_id: int,
        session: AsyncSession,
    ) -> T | None:
        # Найти запись по ID
        logger.info(f"Поиск {cls.model.__name__} с ID: {data_id}")
        try:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись с ID {data_id} найдена.")
            else:
                logger.info(f"Запись с ID {data_id} не найдена.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    @classmethod
    async def find_one_or_none(
        cls,
        session: AsyncSession,
        filters: BaseModel,
    ) -> T | None:
        # Найти одну запись по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            f"Поиск одной записи {cls.model.__name__} по фильтрам: {filter_dict}",
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись найдена по фильтрам: {filter_dict}")
            else:
                logger.info(f"Запись не найдена по фильтрам: {filter_dict}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        filters: BaseModel | None,
    ) -> list[T]:
        if filters:
            filter_dict = filters.model_dump(exclude_unset=True)
        else:
            filter_dict = {}
        logger.info(
            f"Поиск всех записей {cls.model.__name__} по фильтрам: {filter_dict}",
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}",
            )
            raise

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel) -> T:
        # Добавить одну запись
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Добавление записи {cls.model.__name__} с параметрами: {values_dict}",
        )
        new_instance = cls.model(**values_dict)
        session.add(new_instance)
        try:
            await session.flush()
            await session.refresh(new_instance)
            logger.info(f"Запись {cls.model.__name__} успешно добавлена.")
            # todo при успешном коммитится так как TransactionSessionDep
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise e
        return new_instance

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        filters: BaseModel,
        values: BaseModel,
    ) -> int:
        # Обновить записи по фильтрам
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Обновление записей {cls.model.__name__} по фильтру: {filter_dict} с параметрами: {values_dict}",
        )
        query = (
            sqlalchemy_update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_dict.items()])
            .values(**values_dict)
            .execution_options(synchronize_session="fetch")
        )
        try:
            result = await session.execute(query)
            await session.flush()
            logger.info(f"Обновлено {result.rowcount} записей.")
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise e

    @classmethod
    async def delete(cls, session: AsyncSession, filters: BaseModel) -> int:
        # Удалить записи по фильтру
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Удаление записей {cls.model.__name__} по фильтру: {filter_dict}")
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")

        query = sqlalchemy_delete(cls.model).filter_by(**filter_dict)
        try:
            result = await session.execute(query)
            await session.flush()
            logger.info(f"Удалено {result.rowcount} записей.")
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при удалении записей: {e}")
            raise e

    @classmethod
    async def paginate(
        cls,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        filters: BaseModel | None = None,
    ) -> list[T]:
        # Пагинация записей
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(
            f"Пагинация записей {cls.model.__name__} по фильтру: {filter_dict}, страница: {page}, размер страницы: {page_size}",
        )
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(
                query.offset((page - 1) * page_size).limit(page_size),
            )
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей на странице {page}.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при пагинации записей: {e}")
            raise
