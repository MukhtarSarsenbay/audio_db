from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.config import settings
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import create_access_token
from app.crud import create_or_update_user


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

    # Получаем данные о пользователе
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

    # Генерируем внутренний токен
    api_token = create_access_token({"user_id": user.id, "username": user.username})

    return {"api_token": api_token}


@router.get("/refresh_token")
async def refresh_api_token(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    new_token = create_access_token({"user_id": user.id, "username": user.username})
    return {"api_token": new_token}
