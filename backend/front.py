from fastapi import APIRouter, Request, Form, Depends, HTTPException, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import services.user_service as us
from db.supabase import get_db
import services.user_service as us

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_current_user(
    access_token: str = Cookie(None),
    refresh_token: str = Cookie(None),
    db = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Brak access_token")

    try:
        user_resp = db.auth.get_user(access_token)
        print("access_token:", access_token)
        print("refresh_token:", refresh_token)
        return user_resp.user
    except Exception:
        if refresh_token:
            session = db.auth.refresh_session({"refresh_token": refresh_token})
            new_access = session["access_token"]  # nowszy SDK zwraca dict
            user_resp = db.auth.get_user(new_access)
            return user_resp.user
        raise HTTPException(status_code=401, detail="Sesja wygasła")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login_page_post(request: Request, email: str = Form(...), password: str = Form(...), db = Depends(get_db)):
    try:
        auth = db.auth.sign_in_with_password({"email": email, "password": password})
        session = auth.session
        if not session:
            raise HTTPException(status_code=401, detail="Błędne dane logowania")
        response = RedirectResponse(url="/front/edit", status_code=303)
        response.set_cookie("access_token", session.access_token, httponly=True, secure=False)
        response.set_cookie("refresh_token", session.refresh_token, httponly=True, secure=False)
        return response
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": f"Błąd logowania: {str(e)}"
        })

@router.get("/edit", response_class=HTMLResponse)
def edit_page(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse("edit.html", {
        "request": request,
        "message": "",
        "email": current_user.email,
        "username": getattr(current_user, 'username', ''),
        "avatar_url": getattr(current_user, 'avatar_url', '')
    })

@router.post("/edit", response_class=HTMLResponse)
def edit_page_post(
    request: Request,
    email: str = Form(None),
    username: str = Form(None),
    avatar_url: str = Form(None),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        update_data = {}
        if email and email.strip(): update_data["email"] = email.strip()
        if username and username.strip(): update_data["username"] = username.strip()
        if avatar_url and avatar_url.strip(): update_data["avatar_url"] = avatar_url.strip()

        if not update_data:
            return templates.TemplateResponse("edit.html", {
                "request": request,
                "message": "Nie wprowadzono żadnych zmian",
                "email": current_user.email,
                "username": getattr(current_user, 'username', ''),
                "avatar_url": getattr(current_user, 'avatar_url', '')
            })

        from schemas.user import UserUpdate
        payload = UserUpdate(**update_data)
        result = us.edit_user_details(db, payload, current_user)

        return templates.TemplateResponse("edit.html", {
            "request": request,
            "message": "Dane zostały zaktualizowane pomyślnie",
            "email": update_data.get("email", current_user.email),
            "username": update_data.get("username", getattr(current_user, 'username', '')),
            "avatar_url": update_data.get("avatar_url", getattr(current_user, 'avatar_url', ''))
        })

    except HTTPException as e:
        return templates.TemplateResponse("edit.html", {
            "request": request,
            "message": e.detail,
            "email": current_user.email,
            "username": getattr(current_user, 'username', ''),
            "avatar_url": getattr(current_user, 'avatar_url', '')
        })
    except Exception as e:
        return templates.TemplateResponse("edit.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
            "email": current_user.email,
            "username": getattr(current_user, 'username', ''),
            "avatar_url": getattr(current_user, 'avatar_url', '')
        })
