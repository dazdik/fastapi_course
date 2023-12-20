from pydantic import BaseModel, Field


class ToDoSchema(BaseModel):
    title: str = Field(max_length=30)
    description: str
    completed: bool = False
