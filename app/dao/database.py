from datetime import datetime
from typing import Annotated, Any

from sqlalchemy import func, Integer, TIMESTAMP
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.pool import NullPool

from app.core.settings import APP_CONFIG, Environments

# тесты не работаю без NullPool
if APP_CONFIG.environment == Environments.test:
    DATABASE_URL = APP_CONFIG.db.sqlalchemy_test_db_uri
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = APP_CONFIG.db.sqlalchemy_db_uri
    DATABASE_PARAMS = {}

engine = create_async_engine(
    str(DATABASE_URL),
    echo=APP_CONFIG.db.echo,
    **DATABASE_PARAMS,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        """Строковое представление объекта для удобства отладки."""

        fmt = "{}({})"
        class_ = self.__class__.__name__
        attrs = sorted((k, getattr(self, k)) for k in self.__mapper__.columns.keys())
        sattrs = ", ".join("{}={!r}".format(*x) for x in attrs)
        return fmt.format(class_, sattrs)
