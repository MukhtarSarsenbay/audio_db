from fastapi import FastAPI, Depends
from app.config import settings
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes import auth  

app = FastAPI()

app.include_router(auth.router) 

@app.get("/")
def read_root():
    return {"message": "Audio Service API"}

