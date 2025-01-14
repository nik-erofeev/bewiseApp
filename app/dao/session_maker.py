import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.dao.database import async_session_maker

logger = logging.getLogger(__name__)


class DatabaseSessionManager:
    """
    Класс для управления асинхронными сессиями базы данных, включая поддержку транзакций и зависимости FastAPI.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    @asynccontextmanager
    async def create_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Создаёт и предоставляет новую сессию базы данных.
        Гарантирует закрытие сессии по завершении работы.
        """
        async with self.session_maker() as session:
            try:
                yield session
            except Exception as e:
                if not isinstance(e, HTTPException):
                    logger.error(f"Ошибка при создании сессии базы данных: {e=!r}")
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def transaction(self, session: AsyncSession) -> AsyncGenerator[None, None]:
        """
        Управление транзакцией: коммит при успехе, откат при ошибке.
        """
        try:
            yield
            await session.commit()
        except HTTPException:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка транзакции: {e=!r}")
            raise HTTPException(status_code=500, detail="Ошибка транзакции")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Зависимость для FastAPI, возвращающая сессию без управления транзакцией.
        """
        async with self.create_session() as session:
            yield session

    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Зависимость для FastAPI, возвращающая сессию с управлением транзакцией.
        """
        async with self.create_session() as session:
            async with self.transaction(session):
                yield session


# Инициализация менеджера сессий базы данных
session_manager = DatabaseSessionManager(async_session_maker)

# Зависимости FastAPI для использования сессий
SessionDep = Depends(session_manager.get_session)
TransactionSessionDep = Depends(session_manager.get_transaction_session)
