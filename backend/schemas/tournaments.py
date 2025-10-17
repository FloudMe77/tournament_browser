from typing import Optional, List
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

class TournamentParticipant(BaseModel):
    username: str
    role: str  # "creator" or "participant"
    joined_at: Optional[str]

class TournamentMatch(BaseModel):
    match_id: int
    tournament_id: str
    player1_id: str
    player2_id: str
    score: Optional[str]
    date: Optional[datetime]

class TournamentDetails(BaseModel):
    id: str
    name: str
    start_date: str
    created_at: str
    creator_id: str
    creator_username: str
    public: bool
    participants: List[TournamentParticipant]
    matches: List[TournamentMatch]

class TournamentInvitation(BaseModel):
    id: str
    tournament_id: str
    tournament_name: str
    creator_username: str
    start_date: str
    created_at: str
    status: str

class TournamentJoinRequest(BaseModel):
    tournament_id: str

class TournamentInvitationResponse(BaseModel):
    tournament_id: str
    action: str  # "accepted" or "declined"
    