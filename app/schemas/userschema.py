from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str


class CreateUserSchema(UserBaseSchema):
    hashed_password: str = Field(alias="password")


class UserSchema(UserBaseSchema):
    id: int
    is_active: bool = Field(default=False)

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class DataToken(BaseModel):
    id: str | None = None
