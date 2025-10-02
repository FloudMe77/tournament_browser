from typing import List, Optional
from fastapi import Depends, HTTPException, Cookie
from supabase import Client
from schemas.user import User, UserUpdate
from schemas.friend import Invitation
import supabase
from db.supabase import get_db
from schemas.login_form import Login_form
from fastapi import Header, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import services.user_service as us

TABLE_FRIEND = "friendship_request"
def get_friend_list(db: Client, current_user):
    response = (
        db.table("user_friend_list")
        .select("friend_username")
        .eq("user_id", current_user.id)
        .execute()
    )

    friend_list_name = [row["friend_username"] for row in response.data]
    return {"status": "ok", "get": friend_list_name}



def get_invitation_created_by_user(db: Client, current_user):
    response = (
        db.table("invitation_pending_for_user")
        .select("friend_username")
        .eq("user_id", current_user.id)
        .execute()
    )
    friend_list_name = [row["friend_username"] for row in response.data]
    return {"status": "ok", "get": friend_list_name}

def get_invitation_created_for_user(db: Client, current_user):
    response = (
        db.table("invitation_pending_for_user")
        .select("inviter_username")
        .eq("friend_id", current_user.id)
        .execute()
    )
    friend_list_name = [row["inviter_username"] for row in response.data]
    return {"status": "ok", "get": friend_list_name}

def invite_user(db: Client, other_nickname: str, current_user):
    other_id = us.get_user_id_from_name(db=db, name=other_nickname)
    
    response = db.table("user_friend_list") \
        .select("friend_username") \
        .eq("user_id", current_user.id) \
        .eq("friend_username", other_nickname) \
        .execute()
    if response.data:
        return {"status": "error", "message": f"You are already friends with {other_nickname}!"}

    response = db.table("invitation_pending_for_user") \
        .select("inviter_username") \
        .eq("friend_id", current_user.id) \
        .eq("user_id", other_id) \
        .execute()
    if response.data:
        return {"status": "error", "message": f"{other_nickname} has already invited you!"}

    response = db.table("invitation_pending_for_user") \
        .select("inviter_username") \
        .eq("friend_id", other_id) \
        .eq("user_id", current_user.id) \
        .execute()
    if response.data:
        return {"status": "error", "message": f"You have already invited {other_nickname}!"}

    
    data = {"inviter": current_user.id, "invitee": other_id}
    response = db.table(TABLE_FRIEND).insert(data).execute()

    return {"status": "ok", "get": response.data}


def accept_invitation(db: Client, other_nickname: str, current_user):
    current_id = current_user.id
    other_id = us.get_user_id_from_name(db, other_nickname)
    if not other_id:
        return {"status": "error", "message": f"Użytkownik {other_nickname} nie istnieje!"}

    # 1. Sprawdź czy są już znajomymi
    response = db.table("user_friend_list") \
        .select("friend_username") \
        .eq("user_id", current_id) \
        .eq("friend_username", other_nickname) \
        .execute()
    if response.data:
        return {"status": "error", "message": f"Jesteście już znajomymi {other_nickname}!"}

    # 2. Sprawdź czy zaproszenie istnieje
    response = db.table("invitation_pending_for_user") \
        .select("*") \
        .eq("friend_id", current_id) \
        .eq("user_id", other_id) \
        .execute()
    print(current_id, other_id)
    if not response.data:
        return {"status": "error", "message": f"Nie ma takiego zaproszenia od {other_nickname}!"}

    response = ( db.table(TABLE_FRIEND) .update({"status": "accepted"}) .eq("invitee", current_user.id) .eq("inviter", other_id).eq("status", "pending") .execute() )

    return {"status": "ok", "get": response.data}


def reject_invitation(db:Client, other_nickname, current_user):
    current_id = current_user.id
    other_id = us.get_user_id_from_name(db, other_nickname)
    if not other_id:
        return {"status": "error", "message": f"Użytkownik {other_nickname} nie istnieje!"}

    # 1. Sprawdź czy są już znajomymi
    response = db.table("user_friend_list") \
        .select("friend_username") \
        .eq("user_id", current_id) \
        .eq("friend_username", other_nickname) \
        .execute()
    if response.data:
        return {"status": "error", "message": f"Jesteście już znajomymi {other_nickname}!"}

    # 2. Sprawdź czy zaproszenie istnieje
    response = db.table("invitation_pending_for_user") \
        .select("*") \
        .eq("friend_id", current_id) \
        .eq("user_id", other_id) \
        .execute()
    print(current_id, other_id)
    if not response.data:
        return {"status": "error", "message": f"Nie ma takiego zaproszenia od {other_nickname}!"}

    response = ( db.table(TABLE_FRIEND) .update({"status": "rejected"}) .eq("invitee", current_user.id) .eq("inviter", other_id).eq("status", "pending") .execute() )

    return {"status": "ok", "get": response.data}

