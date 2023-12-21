from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_config import get_db_session
from app.models import ToDo
from app.schemas import ToDoSchema

router = APIRouter(prefix="/todo", tags=["ToDO"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_in: ToDoSchema, session: AsyncSession = Depends(get_db_session)
):
    todo = ToDo(**todo_in.model_dump())
    session.add(todo)
    await session.commit()
    return todo


@router.get("/{todo_id}")
async def get_todo_id(todo_id: int, session: AsyncSession = Depends(get_db_session)):
    stmt = await session.execute(select(ToDo).where(ToDo.id == todo_id))
    todo_by_id = stmt.scalar_one_or_none()
    if todo_by_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Id not found"
        )
    return todo_by_id
