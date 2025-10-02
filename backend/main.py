from fastapi import FastAPI
from endpoints import user_auth, menu
import front

app = FastAPI(
    title="Tornament Browser API",
    description="Backend API dla turniejów",
    version="0.0.1"
)

app.include_router(user_auth.router, prefix="/user", tags=["User"])
app.include_router(menu.router, prefix="/menu", tags=["Menu"])


@app.get("/")
def root():
    return {"message": "API działa poprawnie"}
