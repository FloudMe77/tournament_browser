from fastapi import APIRouter, Depends, HTTPException, Header, Cookie, Form
from fastapi.responses import RedirectResponse
import services.user_service as us
from schemas.user import User, UserUpdate
from schemas.login_form import Login_form
from db.supabase import get_db

router = APIRouter()

def get_current_user(
    access_token: str = Cookie(None),
    refresh_token: str = Cookie(None),
    db = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Brak access_token")

    try:
        user = db.auth.get_user(access_token)
        return user.user
    except Exception:
        if refresh_token:
            session = db.auth.refresh_session({"refresh_token": refresh_token})
            new_access = session.session.access_token
            user = db.auth.get_user(new_access)
            return user.user

        raise HTTPException(status_code=401, detail="Sesja wygasła")
    

@router.post("/edit")
def edit(payload: UserUpdate, db=Depends(get_db)):
    return us.edit_user_details(db, payload, get_current_user())

@router.post("/login")
def login_user(email: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    login_data = Login_form(email=email, password=password)
    return us.login_user(db, login_data)

@router.post("/register")
def register(email: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    login_data = Login_form(email=email, password=password)
    return us.register_user(db, login_data)

@router.api_route("/me", methods=["GET", "POST"])
def me(user=Depends(get_current_user)):
    return {"email": user.email, "id": user.id}
