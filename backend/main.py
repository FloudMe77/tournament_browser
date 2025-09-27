from fastapi import FastAPI
from endpoints import user_auth

app = FastAPI(
    title="Tornament Browser API",
    description="Backend API dla turniejów",
    version="0.0.1"
)

app.include_router(user_auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def root():
    return {"message": "API działa poprawnie"}