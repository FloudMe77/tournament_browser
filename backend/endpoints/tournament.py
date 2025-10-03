from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import services.user_service as us
import services.friend_service as fs
import services.tournament as ts
from datetime import datetime, date
from db.supabase import get_db
from utils.auth import get_current_user
from typing import Optional
from schemas.tournaments import Tournament_form, Tournament_edit

router = APIRouter()
templates = Jinja2Templates(directory="templates")
def safe_get(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs).get("get", [])
        except Exception as e:
            return [e.__str__]
        
def get_list_context(db, current_user, message=None):
    data = safe_get(ts.get_user_tournaments, db, current_user)
    data = [{u:v for u,v in tournament_dict.items() if u in ["tournament_name", "start_date", "public", "id"]} for tournament_dict in data]
    return {
        "tournament_created_by_user": data,
        "message": message,
    }


@router.get("/", response_class=HTMLResponse)
def list_page(request: Request, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        context = get_list_context(db, current_user)
        return templates.TemplateResponse("your_tourn.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })
    

    
@router.post("/delete", response_class=HTMLResponse)
def delete_action(request: Request, tournament_id: str = Form(...), db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        result = ts.delete_tournament(db, tournament_id, current_user)
        print(result)
        if result["status"] == "ok":
            message = "Poprawnie usunięto"
        else:
            message = result["message"]
        context = get_list_context(db, current_user, message=message)
        return templates.TemplateResponse("your_tourn.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })
    
@router.post("/create", response_class=HTMLResponse)
def create_action(request: Request, 
                  name: str = Form(...),
                  start_date: str = Form(...),
                  public: Optional[str] = Form(None),
                  db=Depends(get_db),
                  current_user=Depends(get_current_user)):
    try:
        is_public = public is not None  
        form = Tournament_form(name=name, start_date=start_date, public=is_public)
        result = ts.create_new_tournament(db = db, form = form, current_user = current_user)
        print(result)
        if result["status"] == "ok":
            message = "Poprawnie dodano"
        else:
            message = result["message"]
        context = get_list_context(db, current_user, message=message)
        return templates.TemplateResponse("your_tourn.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })


@router.get("/{tournament_id}", response_class=HTMLResponse)
def get_specyfic_tournament(request: Request,
                          tournament_id: str,
                          username_search: str = "",  # query param, domyślnie pusty
                          db=Depends(get_db), 
                          message:Optional[str]=None,
                          current_user=Depends(get_current_user)):
    try:
        ts.verify_user(db=db,tournament_id=tournament_id, current_user=current_user)
        search_results = safe_get(us.get_like_list_users, db, username_search, current_user) if username_search else []
        tournament_data = safe_get(ts.get_tournament,db=db, tournament_id=tournament_id, current_user=current_user)[0]

        invitations_send = safe_get(ts.get_posted_invitation_users,db=db,tournament_id=tournament_id)
        print(invitations_send, "to result")
        

        context = {
            "request": request, 
            "tournament_data": tournament_data, 
            "invitations_send": invitations_send,
            "search_results": search_results,
        }
        if message:
            context["message"] = message

        return templates.TemplateResponse("edit_tourn.html", context)
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })
@router.post("/{tournament_id}/invite", response_class=HTMLResponse)
def invite_user(request: Request, 
                tournament_id: str,
                username_to_invite: str = Form(...),
                db=Depends(get_db),
                current_user=Depends(get_current_user)):
    try:
        ts.verify_user(db=db,tournament_id=tournament_id, current_user=current_user)
        response = ts.invite_user(db, username_to_invite, tournament_id)
        # komunikat do przekazania jako query param
        message = "Wysłano zaproszenie" if response["status"] == "ok" else response["message"]
        return RedirectResponse(
            url=f"/tournament/{tournament_id}?message={message}", 
            status_code=303  # redirect po POST
        )
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })
    
@router.post("/{tournament_id}/update", response_class=HTMLResponse)
def edit_tournament(request: Request, 
                tournament_id: str,
                name: Optional[str] = Form(None),
                start_date: Optional[str] = Form(None),
                public: Optional[str] = Form(None),
                db=Depends(get_db),
                current_user=Depends(get_current_user)):
    try:
        ts.verify_user(db=db,tournament_id=tournament_id, current_user=current_user)
        start_date = start_date or None  
        name = name or None
        is_public = public is not None  

        form = Tournament_edit(
            id=tournament_id,
            name=name,
            start_date=start_date,
            public=is_public
        )

        response = ts.update_tournament(db, form=form, current_user=current_user)

        message = "Pomyślnie zedytowano" if response["status"] == "ok" else response["message"]

        return RedirectResponse(
            url=f"/tournament/{tournament_id}?message={message}", 
            status_code=303
        )
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })
