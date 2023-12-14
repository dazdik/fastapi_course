from pydantic import BaseModel


class ProductSchema(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
