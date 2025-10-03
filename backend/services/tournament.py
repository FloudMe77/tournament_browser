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