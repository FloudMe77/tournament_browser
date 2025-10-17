from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from endpoints import user_auth, menu, tournament, tournament_list
import front

app = FastAPI(
    title="Tournament Browser API",
    description="Backend API dla turniejów",
    version="0.0.1"
)

# Mount static files
app.mount("/static/styles", StaticFiles(directory="styles"), name="static")

app.include_router(user_auth.router, prefix="/user", tags=["User"])
app.include_router(menu.router, prefix="/menu", tags=["Menu"])
app.include_router(tournament.router, prefix="/tournament", tags=["Tournament"])
app.include_router(tournament_list.router, prefix="/tournament_list", tags=["Tournament List"])

@app.get("/")
def root():
    return {"message": "API działa poprawnie"}
