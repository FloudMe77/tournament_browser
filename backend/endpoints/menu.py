from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import services.user_service as us
import services.friend_service as fs
from db.supabase import get_db
from utils.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")
def safe_get(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs).get("get", [])
        except Exception as e:
            return [e.__str__]

def get_menu_context(db, current_user, message=None, search_friend_list=None):
    return {
        "request_invite": safe_get(fs.get_invitation_created_for_user, db, current_user),
        "friends": safe_get(fs.get_friend_list, db, current_user),
        "your_invitation": safe_get(fs.get_invitation_created_by_user, db, current_user),
        "search_friend_list": search_friend_list or [],
        "message": message,
    }


@router.get("/", response_class=HTMLResponse)
def menu_page(request: Request, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        context = get_menu_context(db, current_user)
        return templates.TemplateResponse("menu.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })


@router.post("/", response_class=HTMLResponse)
def menu_page_with_search(request: Request, username_search: str = Form(...),
                          db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        search_results = safe_get(us.get_like_list_users,db, username_search, current_user)
        context = get_menu_context(db, current_user, search_friend_list=search_results)
        return templates.TemplateResponse("menu.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })


def handle_invitation_action(db, current_user, action_func, username, success_message, request):
    """Pomocnicza funkcja do obsługi zaproszeń, akceptacji i odrzucenia."""
    try:
        response = action_func(db, username, current_user)
        message = success_message if response["status"] == "ok" else response["message"]
        context = get_menu_context(db, current_user, message=message)
        return templates.TemplateResponse("menu.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })


@router.post("/invite", response_class=HTMLResponse)
def invite_user(request: Request, username_to_invite: str = Form(...),
                db=Depends(get_db), current_user=Depends(get_current_user)):
    return handle_invitation_action(db, current_user, fs.invite_user, username_to_invite, "Wysłano zaproszenie", request)


@router.post("/accept", response_class=HTMLResponse)
def accept_invitation(request: Request, username_to_accept: str = Form(...),
                      db=Depends(get_db), current_user=Depends(get_current_user)):
    return handle_invitation_action(db, current_user, fs.accept_invitation, username_to_accept, "Zaakceptowano", request)


@router.post("/reject", response_class=HTMLResponse)
def reject_invitation(request: Request, username_to_reject: str = Form(...),
                      db=Depends(get_db), current_user=Depends(get_current_user)):
    return handle_invitation_action(db, current_user, fs.reject_invitation, username_to_reject, "Odrzucono", request)
