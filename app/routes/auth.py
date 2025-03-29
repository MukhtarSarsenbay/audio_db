from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.config import settings
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import create_access_token
from app.crud import create_or_update_user
import shutil
from fastapi import APIRouter, UploadFile, Depends
from app.auth import get_current_user
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas import UserSchema
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()
YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"

@router.get("/login")
async def yandex_login():
    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": settings.YANDEX_REDIRECT_URI
    }
    auth_url = f"{YANDEX_AUTH_URL}?client_id={params['client_id']}&response_type=code&redirect_uri={params['redirect_uri']}"
    return RedirectResponse(auth_url)


@router.get("/callback")
async def yandex_callback(code: str, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.YANDEX_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.YANDEX_CLIENT_ID,
                "client_secret": settings.YANDEX_CLIENT_SECRET,
                "redirect_uri": settings.YANDEX_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Ошибка авторизации")

    token_data = response.json()
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info = await httpx.AsyncClient().get("https://login.yandex.ru/info", headers=headers)

    if user_info.status_code != 200:
        raise HTTPException(status_code=400, detail="Ошибка получения данных пользователя")

    user_data = user_info.json()
    yandex_id = user_data["id"]
    username = user_data["login"]
    email = user_data.get("default_email")

    user = await create_or_update_user(
        db,
        {
            "yandex_id": yandex_id,
            "username": username,
            "email": email,
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    )

    
    api_token = create_access_token({"user_id": user.id, "username": user.username})

    return {"api_token": api_token}


@router.get("/refresh_token")
async def refresh_token(user=Depends(get_current_user)):
    new_token = create_access_token({"user_id": user.id, "username": user.username})
    return {"api_token": new_token}


@router.post("/upload-audio/")
async def upload_audio(file: UploadFile, user=Depends(get_current_user)):
    file_path = f"uploads/{user.id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "path": file_path}


@router.get("/users/me", response_model=UserSchema)  
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
    
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
   
    user = await db.execute(User.select().where(User.username == form_data.username))
    user = user.scalar_one_or_none()

    if not user or user.password != form_data.password:  # ⚠️ Добавить хеширование пароля!
        raise HTTPException(status_code=400, detail="Incorrect username or password")

   
    access_token = create_access_token({"user_id": user.id, "username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}