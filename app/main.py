from fastapi import FastAPI
from .api.v1.auth.endpoints import router as auth_router
from .api.v1.user.endpoints import router as user_router
from .db.base import Base
from .db.session import engine

Base.metadata.create_all(bind=engine)

app=FastAPI()

@app.get("/")
def main():
    return {"message": "Project is running"}

app.include_router(auth_router)
app.include_router(user_router)