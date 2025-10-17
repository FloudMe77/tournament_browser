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
        

@router.get("/", response_class=HTMLResponse)
def list_page(request: Request, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        invitations = safe_get(ts.get_invitations, db, current_user)
        
        public_tournaments = safe_get(ts.get_public_tournaments, db, current_user)
        print(public_tournaments)
        
        context =  {
            "invatation_tournament": invitations,
            "public_tournament":public_tournaments 
        }
        return templates.TemplateResponse("tournament_join.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })

@router.post("/{tournament_id}/join", response_class=HTMLResponse)
def join_tournament(request: Request, 
                   tournament_id: str,
                   db=Depends(get_db), 
                   current_user=Depends(get_current_user)):
    try:
        result = ts.join_public_tournament(db, tournament_id, current_user)
        message = "Pomyślnie dołączono do turnieju" if result["status"] == "ok" else result["message"]
        
        invitations = safe_get(ts.get_invitations, db, current_user)
        public_tournaments = safe_get(ts.get_public_tournaments, db, current_user)
        
        context = {
            "invatation_tournament": invitations,
            "public_tournament": public_tournaments,
            "message": message
        }
        return templates.TemplateResponse("tournament_join.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })

@router.post("/{tournament_id}/accept", response_class=HTMLResponse)
def accept_invitation(request: Request, 
                     tournament_id: str,
                     db=Depends(get_db), 
                     current_user=Depends(get_current_user)):
    try:
        result = ts.respond_to_invitation(db, tournament_id, current_user, "accepted")
        message = "Pomyślnie zaakceptowano zaproszenie" if result["status"] == "ok" else result["message"]
        
        invitations = safe_get(ts.get_invitations, db, current_user)
        public_tournaments = safe_get(ts.get_public_tournaments, db, current_user)
        
        context = {
            "invatation_tournament": invitations,
            "public_tournament": public_tournaments,
            "message": message
        }
        return templates.TemplateResponse("tournament_join.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })

@router.post("/{tournament_id}/reject", response_class=HTMLResponse)
def reject_invitation(request: Request, 
                     tournament_id: str,
                     db=Depends(get_db), 
                     current_user=Depends(get_current_user)):
    try:
        result = ts.respond_to_invitation(db, tournament_id, current_user, "declined")
        message = "Odrzucono zaproszenie" if result["status"] == "ok" else result["message"]
        
        invitations = safe_get(ts.get_invitations, db, current_user)
        public_tournaments = safe_get(ts.get_public_tournaments, db, current_user)
        
        context = {
            "invatation_tournament": invitations,
            "public_tournament": public_tournaments,
            "message": message
        }
        return templates.TemplateResponse("tournament_join.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })

@router.get("/my-tournaments", response_class=HTMLResponse)
def my_tournaments_page(request: Request, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        tournaments = safe_get(ts.get_user_joined_tournaments, db, current_user)
        
        context = {
            "tournaments": tournaments,
            "current_user": current_user
        }
        return templates.TemplateResponse("my_tournaments.html", {"request": request, **context})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Wystąpił błąd: {str(e)}",
        })

# API Endpoints for REST API
@router.get("/api/available")
def get_available_tournaments_api(db=Depends(get_db), current_user=Depends(get_current_user)):
    """API endpoint to get public tournaments and user invitations"""
    try:
        invitations = safe_get(ts.get_invitations, db, current_user)
        public_tournaments = safe_get(ts.get_public_tournaments, db, current_user)
        
        return {
            "status": "success",
            "data": {
                "public_tournaments": public_tournaments,
                "invitations": invitations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wystąpił błąd: {str(e)}")

@router.post("/api/{tournament_id}/join")
def join_tournament_api(tournament_id: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    """API endpoint to join a public tournament"""
    try:
        result = ts.join_public_tournament(db, tournament_id, current_user)
        if result["status"] == "ok":
            return {"status": "success", "message": "Pomyślnie dołączono do turnieju"}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wystąpił błąd: {str(e)}")

@router.post("/api/{tournament_id}/respond")
def respond_to_invitation_api(tournament_id: str, action: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    """API endpoint to respond to tournament invitation"""
    try:
        if action not in ["accepted", "declined"]:
            raise HTTPException(status_code=400, detail="Nieprawidłowa akcja. Użyj 'accepted' lub 'declined'")
        
        result = ts.respond_to_invitation(db, tournament_id, current_user, action)
        if result["status"] == "ok":
            return {"status": "success", "message": f"Pomyślnie {action} zaproszenie"}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wystąpił błąd: {str(e)}")

@router.get("/api/my-tournaments")
def get_my_tournaments_api(db=Depends(get_db), current_user=Depends(get_current_user)):
    """API endpoint to get tournaments user joined (but did not create)"""
    try:
        tournaments = safe_get(ts.get_user_joined_tournaments, db, current_user)
        return {
            "status": "success",
            "data": tournaments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wystąpił błąd: {str(e)}")