from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(50))
    age: Mapped[int]
    is_subscribed: Mapped[bool | None] = mapped_column(default=None)


class UserAuth(Base):
    username: Mapped[str]
    password: Mapped[str]
    session_token: Mapped[str | None] = mapped_column(default=None)
