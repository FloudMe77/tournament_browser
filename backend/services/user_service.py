from typing import List, Optional
from supabase import Client
from schemas.user import User, UserUpdate
import supabase
from schemas.login_form import Login_form
from fastapi import Header, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

TABLE_NAME = "users"


def list_all_users(db: Client):
    data =  db.table(TABLE_NAME).select("*").execute()
    print(data)


def login_user(supabase_client: Client, data: Login_form):
    try:
        auth = supabase_client.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        session = auth.session
        response = JSONResponse(content={"message": "Zalogowano"})
        response.set_cookie("access_token", session.access_token, httponly=True, secure=False)
        response.set_cookie("refresh_token", session.refresh_token, httponly=True, secure=False)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

def register_user(db: Client, data: Login_form):
    try:
        auth = db.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        session = auth.session
        response = JSONResponse(content={"message": "Konto utworzone i zalogowane"})
        response.set_cookie("access_token", session.access_token, httponly=True, secure=False)
        response.set_cookie("refresh_token", session.refresh_token, httponly=True, secure=False)
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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

