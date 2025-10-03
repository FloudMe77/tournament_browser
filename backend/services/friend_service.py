from typing import Dict, Any
from supabase import Client
from repositories.user_repository import UserRepository
from repositories.friend_repository import FriendRepository


def get_friend_list(db: Client, current_user) -> Dict[str, Any]:
    repo = FriendRepository(db)
    friend_list_name = repo.list_friends_usernames(current_user.id)
    return {"status": "ok", "get": friend_list_name}


def get_invitation_created_by_user(db: Client, current_user) -> Dict[str, Any]:
    repo = FriendRepository(db)
    friend_list_name = repo.list_invitations_created_by_user(current_user.id)
    return {"status": "ok", "get": friend_list_name}


def get_invitation_created_for_user(db: Client, current_user) -> Dict[str, Any]:
    repo = FriendRepository(db)
    friend_list_name = repo.list_invitations_for_user(current_user.id)
    return {"status": "ok", "get": friend_list_name}


def invite_user(db: Client, other_nickname: str, current_user) -> Dict[str, Any]:
    user_repo = UserRepository(db)
    friend_repo = FriendRepository(db)

    other_id = user_repo.get_user_id_by_username(other_nickname)
    if not other_id:
        return {"status": "error", "message": f"Użytkownik {other_nickname} nie istnieje!"}

    if friend_repo.are_already_friends(current_user.id, other_nickname):
        return {"status": "error", "message": f"You are already friends with {other_nickname}!"}

    if friend_repo.invitation_exists_from_other_to_user(current_user.id, other_id):
        return {"status": "error", "message": f"{other_nickname} has already invited you!"}

    if friend_repo.invitation_exists_from_user_to_other(current_user.id, other_id):
        return {"status": "error", "message": f"You have already invited {other_nickname}!"}

    created = friend_repo.create_invitation(inviter_id=current_user.id, invitee_id=other_id)
    return {"status": "ok", "get": created}


def accept_invitation(db: Client, other_nickname: str, current_user) -> Dict[str, Any]:
    user_repo = UserRepository(db)
    friend_repo = FriendRepository(db)

    current_id = current_user.id
    other_id = user_repo.get_user_id_by_username(other_nickname)
    if not other_id:
        return {"status": "error", "message": f"Użytkownik {other_nickname} nie istnieje!"}

    if friend_repo.are_already_friends(current_id, other_nickname):
        return {"status": "error", "message": f"Jesteście już znajomymi {other_nickname}!"}

    if not friend_repo.invitation_exists(inviter_id=other_id, invitee_id=current_id):
        return {"status": "error", "message": f"Nie ma takiego zaproszenia od {other_nickname}!"}

    updated = friend_repo.update_invitation_status(inviter_id=other_id, invitee_id=current_id, from_status="pending", to_status="accepted")
    return {"status": "ok", "get": updated}


def reject_invitation(db: Client, other_nickname: str, current_user) -> Dict[str, Any]:
    user_repo = UserRepository(db)
    friend_repo = FriendRepository(db)

    current_id = current_user.id
    other_id = user_repo.get_user_id_by_username(other_nickname)
    if not other_id:
        return {"status": "error", "message": f"Użytkownik {other_nickname} nie istnieje!"}

    if friend_repo.are_already_friends(current_id, other_nickname):
        return {"status": "error", "message": f"Jesteście już znajomymi {other_nickname}!"}

    if not friend_repo.invitation_exists(inviter_id=other_id, invitee_id=current_id):
        return {"status": "error", "message": f"Nie ma takiego zaproszenia od {other_nickname}!"}

    updated = friend_repo.update_invitation_status(inviter_id=other_id, invitee_id=current_id, from_status="pending", to_status="rejected")
    return {"status": "ok", "get": updated}

