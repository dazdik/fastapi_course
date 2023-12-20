from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Header, status

from app.models import Base, Feedback, User
from app.db_config import engine, session
from app.schemas import SchemaFeedBack, UserSchema


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


@app.post("/create_user", status_code=status.HTTP_201_CREATED)
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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8066,
        reload=True,
        workers=3,
    )
