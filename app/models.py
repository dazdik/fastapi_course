from pydantic import BaseModel, EmailStr, constr


class Feedback(BaseModel):
    name: str
    message: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = constr(
        min_length=8,
        max_length=20
    )
