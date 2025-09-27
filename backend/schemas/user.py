from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    user_id: int 
    username: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None