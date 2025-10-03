from typing import Optional
from pydantic import BaseModel

class Login_form(BaseModel):
    email: str
    password: str

class Login_form_full(BaseModel):
    email: str
    password: str
    username: str