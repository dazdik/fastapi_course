from pydantic import BaseModel, Field


class SchemaFeedBack(BaseModel):
    name: str = Field(max_length=30)
    message: str = Field(max_length=150)
