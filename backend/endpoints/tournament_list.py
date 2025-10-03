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
        