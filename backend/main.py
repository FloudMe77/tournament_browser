from fastapi import FastAPI
from endpoints import user_auth
import front

app = FastAPI(
    title="Tornament Browser API",
    description="Backend API dla turniejów",
    version="0.0.1"
)

app.include_router(user_auth.router, prefix="/auth", tags=["Authentication"])

app.include_router(front.router, prefix="/front", tags=["Frontend"])

@app.get("/")
def root():
    return {"message": "API działa poprawnie"}
