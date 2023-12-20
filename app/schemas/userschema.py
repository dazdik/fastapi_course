from pydantic import BaseModel, EmailStr, conint


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    age: conint(gt=0)
    is_subscribed: bool | None = None


class AunteficatedShema(BaseModel):
    username: str
    password: str
    session_token: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User2Schema(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User2Schema):
    hashed_password: str
