from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ToDo(Base):
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)
