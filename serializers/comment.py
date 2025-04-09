# serializers/comment.py
from pydantic import BaseModel
from typing import Optional

class CommentSchema(BaseModel):
    id: Optional[int] = None
    content: str

    class Config:
        orm_mode = True
