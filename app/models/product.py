from sqlalchemy.orm import Mapped

from .base import Base


class Product(Base):
    product_id: Mapped[int]
    name: Mapped[str]
    category: Mapped[str]
    price: Mapped[float]
