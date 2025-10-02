from typing import List, Optional
from fastapi import Depends, HTTPException, Cookie
from supabase import Client
from schemas.user import User, UserUpdate
import supabase
from db.supabase import get_db
from schemas.login_form import Login_form
from fastapi import Header, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

TABLE_NAME = "users"

def get_user_name(db: Client, id: str):
    response =  db.table(TABLE_NAME).select("username").eq("user_id", id).execute()
    return response

def get_user_id_from_name(db: Client, name: str):
    response =  db.table(TABLE_NAME).select("user_id").eq("username", name).execute()
    return response.data[0]["user_id"]

def list_all_users(db: Client):
    data =  db.table(TABLE_NAME).select("*").execute()
    print(data)


def login_user(data: Login_form, db: Client):
    auth = db.auth.sign_in_with_password({"email": data.email, "password": data.password})
    session = auth.session
    if not session:
        raise HTTPException(status_code=401, detail="Błędne dane logowania")
    response = RedirectResponse(url="/menu", status_code=303)
    response.set_cookie("access_token", session.access_token, httponly=True, secure=False)
    response.set_cookie("refresh_token", session.refresh_token, httponly=True, secure=False)
    return response
    

def register_user(data: Login_form, db: Client):
    auth = db.auth.sign_up({"email": data.email, "password": data.password})
    session = auth.session
    if not session:
        raise HTTPException(status_code=401, detail="Błędne dane logowania")
    response = RedirectResponse(url="/user/menu", status_code=303)
    response.set_cookie("access_token", session.access_token, httponly=True, secure=False)
    response.set_cookie("refresh_token", session.refresh_token, httponly=True, secure=False)
    return response


def edit_user_details(db: Client, payload: UserUpdate, current_user):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    
    check = db.table(TABLE_NAME).select("*").eq("user_id", current_user.id).execute()
    
    if not check.data:
        return {"status": "error", "message": "User not found"}
    
    response = (
        db.table(TABLE_NAME)
        .update(data)
        .eq("user_id", current_user.id)
        .execute()
    )

    
    return {"status": "ok", "update": response.data}

def get_like_list_users(db: Client, prefix:str, current_user):
    prefix = prefix.strip()
    if len(prefix)==0:
        return {"status": "ok", "get": []}
    response = (
        db.table(TABLE_NAME)
        .select("username")
        .ilike("username", f"{prefix}%")
        .neq("user_id", current_user.id)
        .execute()
    )
    user_list = [row["username"] for row in response.data]
    return {"status": "ok", "get": user_list}

