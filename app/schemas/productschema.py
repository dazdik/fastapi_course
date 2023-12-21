from pydantic import BaseModel, PositiveInt, Field


class ProductSchema(BaseModel):
    name: str = Field(max_length=40)
    category: str = Field(max_length=40)
    description: str
    price: float
    count: PositiveInt
