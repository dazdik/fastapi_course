from pydantic import BaseModel, EmailStr, conint


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    age: conint(gt=0)
    is_subscribed: bool | None = None