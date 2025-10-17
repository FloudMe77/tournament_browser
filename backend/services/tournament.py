from typing import Dict, Any
from supabase import Client
from schemas.tournaments import Tournament_form, Tournament_edit
from repositories.tournament_repository import TournamentRepository
from repositories.user_repository import UserRepository
from repositories.friend_repository import FriendRepository


def verify_user(db: Client, tournament_id, current_user):
    tournamentRepository = TournamentRepository(db)
    tournamentRepository.verify_user_tournament(tournament_id=tournament_id, user_id=current_user.id)

def get_tournament(db: Client, tournament_id: str,current_user):
    tournamentRepository = TournamentRepository(db)
    
    if(not tournamentRepository.user_have_same_name_tournament(user_id = current_user.id, id=tournament_id)):
        return {"status": "error", "message": f"Nie masz dostępu do tego turnieju!"}

    tournament_list = tournamentRepository.get_tournament_data(tournament_id=tournament_id)
    if(tournament_list):
        return {"status": "ok", "get": tournament_list}
    else: 
        return {"status": "error", "message": "Turniej nie istnieje"}

def get_user_tournaments(db: Client, current_user):
    tournamentRepository = TournamentRepository(db)
    tournament_list = tournamentRepository.get_user_tournaments(current_user.id)
    return {"status": "ok", "get": tournament_list}

def create_new_tournament(db: Client, form: Tournament_form, current_user):
    tournamentRepository = TournamentRepository(db)
    tournament_name = form.name

    if(tournamentRepository.user_have_same_name_tournament(user_id = current_user.id, name=tournament_name)):
        return {"status": "error", "message": f"Turniej {tournament_name} istnieje!"}
    
    created =  tournamentRepository.create_tournament(form = form, current_user_id = current_user.id)
    return {"status": "ok", "get": created}

def update_tournament(db: Client, form: Tournament_edit, current_user):
    tournamentRepository = TournamentRepository(db)
    
    if(not tournamentRepository.user_have_same_name_tournament(user_id = current_user.id, id = form.id)):
        return {"status": "error", "message": f"Turniej nie istnieje!"}
    print("ble!!!")
    edited = tournamentRepository.update_tournament(form=form, current_user_id=current_user.id)
    return {"status": "ok", "get": edited}

def delete_tournament(db: Client, id: str,  current_user):
    tournamentRepository = TournamentRepository(db)

    if(not tournamentRepository.user_have_same_name_tournament(user_id = current_user.id, id=id)):
        return {"status": "error", "message": f"Turniej nir  istnieje!"}
    print(tournamentRepository.get_user_tournaments(user_id = current_user.id), id)
    created =  tournamentRepository.delate_tournament(id=id, current_user_id = current_user.id)
    return {"status": "ok", "get": created}

def invite_user(db: Client, other_nickname: str, tournament_id:str) -> Dict[str, Any]:
    user_repo = UserRepository(db)
    tournamentRepository = TournamentRepository(db)


    other_id = user_repo.get_user_id_by_username(other_nickname)
    if not other_id:
        return {"status": "error", "message": f"Użytkownik {other_nickname} nie istnieje!"}

    if tournamentRepository.is_already_participant(tournament_id, other_id):
        return {"status": "error", "message": f"You are already friends with {other_nickname}!"}

    if tournamentRepository.invitation_exists(tournament_id, other_id):
        return {"status": "error", "message": f"You already invited {other_nickname}"}

    created = tournamentRepository.create_invitation(tournament_id=tournament_id, invitee_id=other_id)
    return {"status": "ok", "get": created}



def get_posted_invitation_users(db: Client, tournament_id):
    tournamentRepository = TournamentRepository(db)
    posted_invitation_users = tournamentRepository.get_posted_invitation_users(tournament_id=tournament_id)
    return {"status": "ok", "get": posted_invitation_users}

def get_invitations(db: Client, current_user):
    tournamentRepository = TournamentRepository(db)
    posted_invitation_users = tournamentRepository.get_invitations(current_user_id= current_user.id)
    return {"status": "ok", "get": posted_invitation_users}

def get_public_tournaments(db: Client, current_user):
    tournamentRepository = TournamentRepository(db)
    posted_invitation_users = tournamentRepository.get_public_tournament(current_user_id= current_user.id)
    return {"status": "ok", "get": posted_invitation_users}

def join_public_tournament(db: Client, tournament_id: str, current_user) -> Dict[str, Any]:
    tournamentRepository = TournamentRepository(db)
    
    # Check if tournament exists and is public
    tournament_data = tournamentRepository.get_tournament_data(tournament_id)
    if not tournament_data:
        return {"status": "error", "message": "Turniej nie istnieje"}
    
    tournament = tournament_data[0]
    if not tournament.get("public"):
        return {"status": "error", "message": "Ten turniej nie jest publiczny"}
    
    # Check if user is already enrolled
    if tournamentRepository.is_already_participant(tournament_id, current_user.id):
        return {"status": "error", "message": "Już jesteś uczestnikiem tego turnieju"}
    
    # Check if there's already a pending invitation
    if tournamentRepository.invitation_exists(tournament_id, current_user.id):
        return {"status": "error", "message": "Masz już oczekujące zaproszenie do tego turnieju"}
    
    # Create tournament_request with status='accepted'
    data = {
        "tournament_id": tournament_id, 
        "invitee": current_user.id,
        "status": "accepted"
    }
    response = db.table("tournament_request").insert(data).execute()
    
    if response.data:
        return {"status": "ok", "get": response.data}
    else:
        return {"status": "error", "message": "Nie udało się dołączyć do turnieju"}

def respond_to_invitation(db: Client, tournament_id: str, current_user, action: str) -> Dict[str, Any]:
    tournamentRepository = TournamentRepository(db)
    
    print(f"DEBUG: Looking for invitation for tournament {tournament_id}, user {current_user.id}")
    
    # Find the pending invitation - try both tables
    response = (
        db.table("tournament_request")
        .select("*")
        .eq("tournament_id", tournament_id)
        .eq("invitee", current_user.id)
        .eq("status", "pending")
        .execute()
    )
    
    
    # If not found, try the invitation view
    if not response.data:
        response = (
            db.table("tournaments_invitations")
            .select("*")
            .eq("tournament_id", tournament_id)
            .eq("invitee", current_user.id)
            .eq("status", "pending")
            .execute()
        )
    
    if not response.data:
        return {"status": "error", "message": "Nie znaleziono oczekującego zaproszenia"}
    
    # Update the invitation status in tournament_request table
    update_response = (
        db.table("tournament_request")
        .update({"status": action})
        .eq("tournament_id", tournament_id)
        .eq("invitee", current_user.id)
        .eq("status", "pending")
        .execute()
    )
    
    
    if update_response.data:
        return {"status": "ok", "get": update_response.data}
    else:
        return {"status": "error", "message": f"Nie udało się {action} zaproszenia"}

def get_user_enrolled_tournaments(db: Client, current_user):
    tournamentRepository = TournamentRepository(db)
    
    # Get tournaments created by user
    created_tournaments = tournamentRepository.get_user_tournaments(current_user.id)
    
    # Get tournaments where user has accepted invitations
    accepted_invitations = (
        db.table("tournament_request")
        .select("tournament_id")
        .eq("invitee", current_user.id)
        .eq("status", "accepted")
        .execute()
    )
    
    accepted_tournament_ids = [inv["tournament_id"] for inv in (accepted_invitations.data or [])]
    
    # Get tournament details for accepted invitations
    enrolled_tournaments = []
    if accepted_tournament_ids:
        enrolled_response = (
            db.table("tournament_created_by_user")
            .select("*")
            .in_("id", accepted_tournament_ids)
            .execute()
        )
        enrolled_tournaments = enrolled_response.data or []
    
    # Combine both lists and remove duplicates
    all_tournaments = created_tournaments + enrolled_tournaments
    unique_tournaments = []
    seen_ids = set()
    
    for tournament in all_tournaments:
        if tournament["id"] not in seen_ids:
            # Add participant count
            participant_count = get_tournament_participant_count(db, tournament["id"])
            tournament["participant_count"] = participant_count
            
            # Add tournament status
            tournament["status"] = get_tournament_status(tournament["start_date"])
            
            unique_tournaments.append(tournament)
            seen_ids.add(tournament["id"])
    
    return {"status": "ok", "get": unique_tournaments}


def get_user_joined_tournaments(db: Client, current_user):
    tournamentRepository = TournamentRepository(db)
    
    # Get tournaments created by user
    created_tournaments = tournamentRepository.get_user_tournaments(current_user.id)
    
    # Get tournaments where user has accepted invitations
    accepted_invitations = (
        db.table("tournament_request")
        .select("tournament_id")
        .eq("invitee", current_user.id)
        .eq("status", "accepted")
        .execute()
    )
    
    accepted_tournament_ids = [inv["tournament_id"] for inv in (accepted_invitations.data or [])]
    
    # Get tournament details for accepted invitations
    joined_tournaments = []
    if accepted_tournament_ids:
        joined_response = (
            db.table("tournament_created_by_user")
            .select("*")
            .in_("id", accepted_tournament_ids)
            .execute()
        )
        joined_tournaments = joined_response.data or []
    
    # Combine both lists and remove duplicates
    all_tournaments = created_tournaments + joined_tournaments
    unique_tournaments = []
    seen_ids = set()
    
    for tournament in all_tournaments:
        if tournament["id"] not in seen_ids:
            # Add participant count
            participant_count = get_tournament_participant_count(db, tournament["id"])
            tournament["participant_count"] = participant_count
            
            # Add tournament status
            tournament["status"] = get_tournament_status(tournament["start_date"])
            
            unique_tournaments.append(tournament)
            seen_ids.add(tournament["id"])
    
    return {"status": "ok", "get": unique_tournaments}

def get_tournament_participant_count(db: Client, tournament_id: str) -> int:
    # Count creators + accepted invitations
    creator_count = 1  # Tournament always has a creator
    
    accepted_count = (
        db.table("tournament_request")
        .select("id", count="exact")
        .eq("tournament_id", tournament_id)
        .eq("status", "accepted")
        .execute()
    )
    
    return creator_count + (accepted_count.count or 0)

def get_tournament_status(start_date_str: str) -> str:
    from datetime import datetime
    
    try:
        # Parse the start date (assuming it's in ISO format)
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        now = datetime.now(start_date.tzinfo) if start_date.tzinfo else datetime.now()
        
        # Add some buffer time for tournament status
        buffer_hours = 2
        
        if now < start_date:
            return "upcoming"
        elif now < start_date.replace(hour=start_date.hour + buffer_hours):
            return "ongoing"
        else:
            return "finished"
    except Exception:
        return "unknown"

def get_tournament_participants(db: Client, tournament_id: str):
    tournamentRepository = TournamentRepository(db)
    participants = tournamentRepository.get_tournament_participants(tournament_id)
    return {"status": "ok", "get": participants}

def get_tournament_matches(db: Client, tournament_id: str):
    tournamentRepository = TournamentRepository(db)
    matches = tournamentRepository.get_tournament_matches(tournament_id)
    return {"status": "ok", "get": matches}