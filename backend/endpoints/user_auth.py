from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import services.user_service as us
from schemas.login_form import Login_form
from db.supabase import get_db
from utils.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def build_edit_context(current_user, message: str = ""):
    return {
        "message": message,
        "email": current_user.email,
        "username": getattr(current_user, 'username', ''),
        "avatar_url": getattr(current_user, 'avatar_url', '')
    }


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
def login_page_post(request: Request, email: str = Form(...), password: str = Form(...), db = Depends(get_db)):
    try:
        return us.login_user(Login_form(email=email, password=password), db)
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": f"Błąd logowania: {str(e)}"
        })


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
def register_page_post(request: Request, email: str = Form(...), password: str = Form(...), db = Depends(get_db)):
    try:
        return us.register_user(Login_form(email=email, password=password), db)
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": f"Błąd logowania: {str(e)}"
        })


@router.get("/edit", response_class=HTMLResponse)
def edit_page(request: Request, current_user = Depends(get_current_user)):
    context = build_edit_context(current_user)
    return templates.TemplateResponse("edit.html", {"request": request, **context})


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
            context = build_edit_context(current_user, message="Nie wprowadzono żadnych zmian")
            return templates.TemplateResponse("edit.html", {"request": request, **context})

        from schemas.user import UserUpdate
        payload = UserUpdate(**update_data)
        us.edit_user_details(db, payload, current_user)

        context = build_edit_context(current_user)
        context.update({
            "message": "Dane zostały zaktualizowane pomyślnie",
            "email": update_data.get("email", context["email"]),
            "username": update_data.get("username", context["username"]),
            "avatar_url": update_data.get("avatar_url", context["avatar_url"]),
        })
        return templates.TemplateResponse("edit.html", {"request": request, **context})

    except HTTPException as e:
        context = build_edit_context(current_user, message=e.detail)
        return templates.TemplateResponse("edit.html", {"request": request, **context})
    except Exception as e:
        context = build_edit_context(current_user, message=f"Wystąpił błąd: {str(e)}")
        return templates.TemplateResponse("edit.html", {"request": request, **context})
