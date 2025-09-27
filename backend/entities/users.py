from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
import uuid

def pk() -> str:
    return uuid.uuid4().hex

class Users(SQLModel, table = True):
    user_id: int = Field(default_factory=pk, primary_key=True)
    username: Optional[str] = Field(default=None, max_length=1000)
    avatar: Optional[str] = Field(default=None, max_length=1000)
    email: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class UsersEdit(SQLModel, table = True):
    username: Optional[str] = Field(default=None, max_length=1000)
    avatar: Optional[str] = Field(default=None, max_length=1000)
    email: Optional[str] = Field(default=None, max_length=1000)