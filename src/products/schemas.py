from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field

from src.products.types import CommentId


class CommentIn(BaseModel):
    message: str


class CommentList(CommentIn):
    id: CommentId
    username: str
    created_at: Annotated[datetime, Field(serialization_alias="createdAt")]
