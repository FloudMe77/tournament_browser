
from typing import Optional
from fastapi import Depends, HTTPException, Cookie
from db.supabase import get_db


def get_current_user(
    access_token: Optional[str] = Cookie(None),
    refresh_token: Optional[str] = Cookie(None),
    db = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Brak access_token")

    try:
        user_resp = db.auth.get_user(access_token)
        return user_resp.user
    except Exception:
        if refresh_token:
            session = db.auth.refresh_session({"refresh_token": refresh_token})
            new_access = session["access_token"]
            user_resp = db.auth.get_user(new_access)
            return user_resp.user
        raise HTTPException(status_code=401, detail="Sesja wygasła")
