from fastapi import FastAPI, Depends
from app.config import settings
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Audio Service API"}



@app.get("/config_test")
def config_test():
    return {
        "database_url": settings.DATABASE_URL,
        "yandex_client_id": settings.YANDEX_CLIENT_ID
    }

@app.get("/test_secret")
def test_secret():
    return {"secret_key": settings.SECRET_KEY}


from sqlalchemy import text

@app.get("/test_db")
async def test_db(session: AsyncSession = Depends(get_db)):
    try:
        await session.execute(text("SELECT 1"))  # Use text() to avoid the error
        return {"status": "Database connected successfully!"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
    
@app.get("/check-env")
async def check_env():
    return {
        "DATABASE_URL": settings.DATABASE_URL,
        "SECRET_KEY": settings.SECRET_KEY[:5] + "***",
        "YANDEX_CLIENT_ID": settings.YANDEX_CLIENT_ID[:5] + "***"
    }