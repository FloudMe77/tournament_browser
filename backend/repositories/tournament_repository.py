from typing import List, Optional, Dict, Any
from supabase import Client
from schemas.tournaments import Tournament_form, Tournament_edit
from fastapi import HTTPException, status

TOURNAMENT_TABLE = "tournaments"
TOURNAMENT_REQUEST_TABLE = "tournament_request"
USER_TOURNAMENT_VIEW = "tournament_created_by_user"
INVITATION_VIEW = "tournaments_invitations"

class TournamentRepository:
    def __init__(self, db: Client) -> None:
        self._db = db

    def verify_user_tournament(self, tournament_id: str, user_id: str):
        response = (
            self._db.table(TOURNAMENT_TABLE)
            .select("*")
            .eq("creator_id", user_id)
            .eq("id", tournament_id)
            .execute()
        )
        if not response:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nie masz do tego dostępu"
            )

    def get_tournament_data(self, tournament_id: str):
        response = (
            self._db.table(TOURNAMENT_TABLE)
            .select("*")
            .eq("id", tournament_id)
            .order("start_date")
            .execute()
        )
        print(response.data)
        return response.data

    def get_user_tournaments(self, user_id: str):
        
        response = (
            self._db.table(USER_TOURNAMENT_VIEW)
            .select("*")
            .eq("creator_id", user_id)
            .order("start_date")
            .execute()
        )
        return response.data

    def user_have_same_name_tournament(self, user_id: str, name:Optional[str] = None, id: Optional[str] = None):
        if (name and id) or (not name and not id):
            raise Exception    
        response = None    
        if(name):
            response = (
                self._db.table(USER_TOURNAMENT_VIEW)
                .select("*")
                .eq("creator_id", user_id)
                .eq("tournament_name", name)
                .execute()
            )
        if(id):
            response = (
                self._db.table(USER_TOURNAMENT_VIEW)
                .select("*")
                .eq("creator_id", user_id)
                .eq("id", id)
                .execute()
            )
        return bool(response.data) 
    
    def create_tournament(self, form: Tournament_form, current_user_id: str):
        
        data = form.model_dump()
        data["creator_id"] = current_user_id
        print(data)
        response = self._db.table(TOURNAMENT_TABLE).insert(data).execute()
        return response.data or []
    
    def update_tournament(self, form: Tournament_edit, current_user_id: str):
        data = {u:v for u,v in form.model_dump().items() if v is not None}
        print(data, "to update")
        response = (
            self._db.table(TOURNAMENT_TABLE)
            .update(data)
            .eq("creator_id", current_user_id)
            .execute()
        )
        return response.data or []
    
    def delate_tournament(self, id: str, current_user_id: str):
        response = (
            self._db.table(TOURNAMENT_TABLE)
            .delete()
            .eq("creator_id", current_user_id)
            .eq("id", id)
            .execute()
        )
        return response.data
    
    
    def is_already_participant(self, tournament_id:str, other_user_id:str):
        response = (
            self._db.table(INVITATION_VIEW)
            .select("*")
            .eq("invitee", other_user_id)
            .eq("tournament_id", tournament_id)
            .eq("status", "accepted")
            .execute()
        )
        return bool(response.data)
    
    def invitation_exists(self, tournament_id:str, other_user_id:str):
        response = (
            self._db.table(INVITATION_VIEW)
            .select("*")
            .eq("invitee", other_user_id)
            .eq("tournament_id", tournament_id)
            .eq("status", "pending")
            .execute()
        )
        return bool(response.data)
    
    def create_invitation(self, tournament_id, invitee_id):
        data = {"tournament_id": tournament_id, "invitee": invitee_id}
        response = self._db.table(TOURNAMENT_REQUEST_TABLE).insert(data).execute()
        return response.data or []
    
    def get_posted_invitation_users(self, tournament_id):
        response = (
            self._db.table(INVITATION_VIEW)
            .select("invitee_username")
            .eq("tournament_id", tournament_id)
            .eq("status", "pending")
            .execute()
        )
        return [row["invitee_username"] for row in (response.data or [])]
    
    def get_invitations(self, current_user_id):
        response = (
            self._db.table(INVITATION_VIEW)
            .select("*")
            .eq("invitee", current_user_id)
            .eq("status", "pending")
            .execute()
        )
        return response.data
    
    def get_public_tournament(self, current_user_id: str):
        tournaments = (
            self._db.table(USER_TOURNAMENT_VIEW)
            .select("*")
            .eq("public", True)
            .execute()
        ).data

        invitations = (
            self._db.table(INVITATION_VIEW)
            .select("tournament_id, status")
            .eq("invitee", current_user_id)
            .in_("status", ["pending", "accepted"])
            .execute()
        ).data

        invited_ids = {inv["tournament_id"] for inv in invitations}

        result = [t for t in tournaments if t["id"] not in invited_ids]
        return result
