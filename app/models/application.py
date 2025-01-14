from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.dao.database import Base, str_uniq


class Application(Base):
    user_name: Mapped[str_uniq]
    description: Mapped[str] = mapped_column(Text, nullable=False)
