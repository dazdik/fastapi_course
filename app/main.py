import re
import secrets
from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import (Cookie, FastAPI, Header, HTTPException, Query, Request,
                     Response, status)
from sqlalchemy import select

from app.models import Base, Feedback, Product, User, UserAuth
from app.models.config import engine, session
from app.schemas import (AunteficatedShema, ProductSchema, SchemaFeedBack,
                         UserSchema)


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
async def create_user(people: UserSchema) -> UserSchema:
    async with session() as s:
        user = User(
            name=people.name,
            email=people.email,
            age=people.age,
            is_subscribed=people.is_subscribed,
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


@app.post("/login")
async def root(response: Response, user: AunteficatedShema):
    async with session() as s:
        res = select(UserAuth).filter(
            user.username == UserAuth.username, user.password == UserAuth.password
        )
        result = await s.execute(res)
        result_user = result.scalar_one_or_none()
        if result_user is None:
            raise HTTPException(status_code=401, detail="message: Unauthorized")
        session_token = secrets.token_urlsafe()
        response.set_cookie(
            key="session_token", value=session_token, httponly=True, secure=True
        )
        result_user.session_token = session_token
        await s.commit()
    return {"message": "куки установлены"}


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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8066,
        reload=True,
        workers=3,
    )
