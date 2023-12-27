from pydantic import BaseModel, PositiveInt, Field, PositiveFloat


class ProductSchema(BaseModel):
    name: str = Field(max_length=40)
    category: str = Field(max_length=40)
    description: str
    price: float
    count: PositiveInt = 1


class Item(BaseModel):
    name: str
    description: str | None = None
    price: PositiveFloat
