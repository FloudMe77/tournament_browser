from pydantic import BaseModel

class Invitation(BaseModel):
    invitee : str
    inviter: str
    status: str = "pending"