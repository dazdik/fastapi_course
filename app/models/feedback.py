from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Feedback(Base):
    name: Mapped[str] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(String(150))
