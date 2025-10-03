from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import services.user_service as us
import services.tournament as ts
from db.supabase import get_db
from utils.auth import get_current_user
from schemas.tournaments import Tournament_form, Tournament_edit

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def safe_get(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs).get("get", [])
    except Exception as e:
        return [str(e)]


def render_template(template: str, request: Request, **context):
    return templates.TemplateResponse(template, {"request": request, **context})


def render_error(request: Request, error: Exception):
    return render_template("error.html", request, message=f"Wystąpił błąd: {str(error)}")


def get_list_context(db, current_user, message: Optional[str] = None):
    tournaments = safe_get(ts.get_user_tournaments, db, current_user)
    simplified = [
        {k: v for k, v in t.items() if k in ["tournament_name", "start_date", "public", "id"]}
        for t in tournaments
    ]
    return {
        "tournament_created_by_user": simplified,
        "message": message,
    }


@router.get("/", response_class=HTMLResponse)
def list_page(request: Request, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        context = get_list_context(db, current_user)
        return render_template("your_tourn.html", request, **context)
    except Exception as e:
        return render_error(request, e)


@router.post("/delete", response_class=HTMLResponse)
def delete_tournament(request: Request, 
                      tournament_id: str = Form(...),
                      db=Depends(get_db),
                      current_user=Depends(get_current_user)):
    try:
        result = ts.delete_tournament(db, tournament_id, current_user)
        message = "Poprawnie usunięto" if result["status"] == "ok" else result["message"]
        context = get_list_context(db, current_user, message)
        return render_template("your_tourn.html", request, **context)
    except Exception as e:
        return render_error(request, e)


@router.post("/create", response_class=HTMLResponse)
def create_tournament(request: Request,
                      name: str = Form(...),
                      start_date: str = Form(...),
                      public: Optional[str] = Form(None),
                      db=Depends(get_db),
                      current_user=Depends(get_current_user)):
    try:
        form = Tournament_form(name=name, start_date=start_date, public=(public is not None))
        result = ts.create_new_tournament(db, form=form, current_user=current_user)
        message = "Poprawnie dodano" if result["status"] == "ok" else result["message"]
        context = get_list_context(db, current_user, message)
        return render_template("your_tourn.html", request, **context)
    except Exception as e:
        return render_error(request, e)


@router.get("/{tournament_id}", response_class=HTMLResponse)
def edit_tournament_page(request: Request,
                         tournament_id: str,
                         username_search: str = "",
                         db=Depends(get_db),
                         message: Optional[str] = None,
                         current_user=Depends(get_current_user)):
    try:
        ts.verify_user(db=db, tournament_id=tournament_id, current_user=current_user)

        search_results = (
            safe_get(us.get_like_list_users, db, username_search, current_user)
            if username_search else []
        )
        tournament_data = safe_get(ts.get_tournament, db=db, tournament_id=tournament_id, current_user=current_user)[0]
        invitations_send = safe_get(ts.get_posted_invitation_users, db=db, tournament_id=tournament_id)

        context = {
            "tournament_data": tournament_data,
            "invitations_send": invitations_send,
            "search_results": search_results,
            "message": message,
        }
        return render_template("edit_tourn.html", request, **context)
    except Exception as e:
        return render_error(request, e)


@router.post("/{tournament_id}/invite", response_class=HTMLResponse)
def invite_user(request: Request,
                tournament_id: str,
                username_to_invite: str = Form(...),
                db=Depends(get_db),
                current_user=Depends(get_current_user)):
    try:
        ts.verify_user(db=db, tournament_id=tournament_id, current_user=current_user)
        response = ts.invite_user(db, username_to_invite, tournament_id)
        message = "Wysłano zaproszenie" if response["status"] == "ok" else response["message"]

        return RedirectResponse(
            url=f"/tournament/{tournament_id}?message={message}",
            status_code=303
        )
    except Exception as e:
        return render_error(request, e)


@router.post("/{tournament_id}/update", response_class=HTMLResponse)
def update_tournament(request: Request,
                      tournament_id: str,
                      name: Optional[str] = Form(None),
                      start_date: Optional[str] = Form(None),
                      public: Optional[str] = Form(None),
                      db=Depends(get_db),
                      current_user=Depends(get_current_user)):
    try:
        ts.verify_user(db=db, tournament_id=tournament_id, current_user=current_user)

        form = Tournament_edit(
            id=tournament_id,
            name=name or None,
            start_date=start_date or None,
            public=(public is not None)
        )

        response = ts.update_tournament(db, form=form, current_user=current_user)
        message = "Pomyślnie zedytowano" if response["status"] == "ok" else response["message"]

        return RedirectResponse(
            url=f"/tournament/{tournament_id}?message={message}",
            status_code=303
        )
    except Exception as e:
        return render_error(request, e)
