from pydantic import BaseModel, EmailStr, PositiveInt


class Feedback(BaseModel):
    name: str
    message: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: PositiveInt = None
    is_subscribed: bool = None
