from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_config import get_db_session
from app.models import User
from app.schemas import CreateUserSchema

router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pass(password: str):
    return pwd_context.hash(password)


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: CreateUserSchema, session: AsyncSession = Depends(get_db_session)
):
    hashed_pass = hash_pass(user_in.hashed_password)

    user = User(
        email=user_in.email,
        password=hashed_pass,
        username=user_in.username,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_users(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    stmt = await session.execute(select(User).where(User.id == user_id))

    user = stmt.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="id not found"
        )

    return {"user_id": user.id, "username": user.username, "email": user.email}
