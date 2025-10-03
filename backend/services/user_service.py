from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from supabase import Client
from schemas.user import UserUpdate
from schemas.login_form import Login_form
from fastapi.responses import RedirectResponse

from repositories.user_repository import UserRepository




def get_user_name(db: Client, id: str) -> Dict[str, Any]:
    repo = UserRepository(db)
    username = repo.get_username_by_id(id)
    if username is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username}


def get_user_id_from_name(db: Client, name: str) -> str:
    repo = UserRepository(db)
    user_id = repo.get_user_id_by_username(name)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_id


def user_exist(db: Client) -> List[Dict[str, Any]]:
    repo = UserRepository(db)
    return repo.list_all()


def login_user(data: Login_form, db: Client) -> RedirectResponse:
    auth = db.auth.sign_in_with_password({"email": data.email, "password": data.password})
    session = auth.session
    if not session:
        raise HTTPException(status_code=401, detail="Błędne dane logowania")
    response = RedirectResponse(url="/menu", status_code=303)
    response.set_cookie("access_token", session.access_token, httponly=True, secure=False)
    response.set_cookie("refresh_token", session.refresh_token, httponly=True, secure=False)
    return response


def register_user(data: Login_form, db: Client) -> RedirectResponse:
    auth = db.auth.sign_up({"email": data.email, "password": data.password})
    session = auth.session
    if not session:
        raise HTTPException(status_code=401, detail="Błędne dane logowania")
    response = RedirectResponse(url="/user/menu", status_code=303)
    response.set_cookie("access_token", session.access_token, httponly=True, secure=False)
    response.set_cookie("refresh_token", session.refresh_token, httponly=True, secure=False)
    return response


def edit_user_details(db: Client, payload: UserUpdate, current_user) -> Dict[str, Any]:
    repo = UserRepository(db)
    data = {k: v for k, v in payload.model_dump().items() if v is not None}

    current = repo.get_by_user_id(current_user.id)
    if current is None:
        return {"status": "error", "message": "User not found"}

    updated = repo.update_by_user_id(current_user.id, data)
    return {"status": "ok", "update": updated}


def get_like_list_users(db: Client, prefix: str, current_user) -> Dict[str, Any]:
    repo = UserRepository(db)
    prefix = prefix.strip()
    if len(prefix) == 0:
        return {"status": "ok", "get": []}

    usernames = repo.search_usernames_prefix_excluding_user(prefix, current_user.id)
    return {"status": "ok", "get": usernames}

