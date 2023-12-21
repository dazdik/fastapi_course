from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Product(Base):
    name: Mapped[str]
    category: Mapped[str]
    description: Mapped[str] = mapped_column(default="", server_default="")
    price: Mapped[float]
    count: Mapped[int] = mapped_column(default=1, server_default="1")
