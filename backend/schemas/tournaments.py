from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Tournament_form(BaseModel):
    name: str
    start_date: str
    public: bool = True
    
class Tournament_edit(BaseModel):
    id: str
    name: Optional[str]
    start_date: Optional[str]
    public: Optional[bool] 

class Tournament_front(BaseModel):
    name: str
    start_date: str
    public: bool
    