from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html",{"request": request,})

@router.get("/edit", response_class=HTMLResponse)
def edit_page(request: Request):
    return templates.TemplateResponse("edit.html",{"request": request,})

@router.post("/login", response_class=HTMLResponse)
def login_page_post(request: Request, ):
    try:
        res = RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        return RedirectResponse(url="front/login", status_code=303)
    return RedirectResponse(url="front/edit", status_code=303)
