import re
import bcrypt
from contextlib import asynccontextmanager
from datetime import timedelta, datetime
from typing import Annotated

import jwt
import uvicorn
from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import select

from app.models import Base, Feedback, Product, UserAuth, ToDo
from app.db_config import engine, session
from app.schemas import (
    AunteficatedShema,
    ProductSchema,
    SchemaFeedBack,
    User2Schema,
    UserInDB,
    Token,
    TokenData,
    ToDoSchema,
)
from jwt import PyJWTError
from passlib.context import CryptContext


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    # Clean up the ML models and release the resources
    pass


app = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "be1310020364b6fef23410fc4eb85100d00083306899ab8abf3bed0243deb1a9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "pythondev": {
        "username": "python",
        "full_name": "Python Developer",
        "email": "pythondev@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
}


@app.get("/items/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}


@app.post("/feedback/", status_code=status.HTTP_201_CREATED)
async def create_feedback(feedback: SchemaFeedBack) -> dict:
    async with session() as s:
        feed = Feedback(name=feedback.name, message=feedback.message)
        s.add(feed)
        await s.commit()
    return {"message": f"Feedback received. Thank you, {feed.name}!"}


@app.post(
    "/create_user",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: AunteficatedShema) -> AunteficatedShema:
    async with session() as s:
        user = UserAuth(
            username=user.username,
            password=user.password,
            session_token=user.session_token,
        )
        s.add(user)
        await s.commit()
    return user


@app.post(
    "/create_products/",
    status_code=status.HTTP_201_CREATED,
)
async def create_product(product: ProductSchema) -> ProductSchema:
    async with session() as s:
        product = Product(
            product_id=product.product_id,
            name=product.name,
            category=product.category,
            price=product.price,
        )
        s.add(product)
        await s.commit()
        return product


@app.get("/product/{product_id}")
async def get_product_by_id(product_id: int) -> ProductSchema:
    async with session() as s:
        stmt = await s.execute(select(Product).filter(Product.product_id == product_id))
        product = stmt.scalar_one_or_none()
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="id not found"
            )
        return product


@app.get("/products/search")
async def search_exactly_product(
    keyword: str,
    category: str | None = None,
    limit: int = Query(10, le=10),
) -> list[ProductSchema]:
    async with session() as s:
        stmt = select(Product).where(Product.name.ilike(f"%{keyword}%"))

        if category:
            stmt = stmt.where(Product.category.ilike(f"%{category}%"))
        stmt = stmt.limit(limit)
        result = await s.execute(stmt)
        products = result.scalars().all()
        return products


async def get_user_from_db(user: AunteficatedShema) -> AunteficatedShema:
    async with session() as s:
        res = select(UserAuth).filter(
            user.username == UserAuth.username, user.password == UserAuth.password
        )
        result = await s.execute(res)
        result_user = result.scalar_one_or_none()
        if result_user is None:
            raise HTTPException(status_code=401, detail="message: Unauthorized")

        return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User2Schema, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected_resource", response_model=User2Schema)
async def read_users_me(
    current_user: Annotated[User2Schema, Depends(get_current_active_user)]
):
    return current_user


@app.get("/user")
async def user_true(session_token: str = Cookie(None)):
    if session_token is None:
        return {"message": "Токен сессии отсутствует"}

    async with session() as s:
        query = select(UserAuth).where(UserAuth.session_token == session_token)
        result = await s.execute(query)
        user = result.scalar_one_or_none()

        if user:
            return {"user_info": f"{user.username}"}
        else:
            return {"message": "Пользователь не найден или токен недействителен"}


ACCEPT_LANGUAGE_PATTERN = (
    r"(?i:(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?,)+(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?"
)


@app.get("/headers")
async def get_headers(request: Request):
    headers = request.headers
    user_agent = headers.get("User-Agent")
    accept_language = headers.get("Accept-Language")
    if user_agent is None and accept_language is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="необходимые заголовки отсутствуют",
        )
    if not re.match(ACCEPT_LANGUAGE_PATTERN, accept_language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="неправильный формат Accept-Language",
        )
    return {"User-Agent": user_agent, "Accept-Language": accept_language}


@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo_in: ToDoSchema) -> ToDoSchema:
    async with session() as s:
        todo = ToDo(
            title=todo_in.title,
            description=todo_in.description,
            completed=todo_in.completed,
        )
        s.add(todo)
        await s.commit()
        return todo


@app.get("/todos/{todo_id}")
async def get_todo_id(todo_id: int) -> ToDoSchema:
    async with session() as s:
        stmt = await s.execute(select(ToDo).where(ToDo.id == todo_id))
        todo_by_id = stmt.scalar_one_or_none()
        if todo_by_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Id not found"
            )
        return todo_by_id


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8066,
        reload=True,
        workers=3,
    )
