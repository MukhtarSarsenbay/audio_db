from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User

async def get_user_by_yandex_id(db: AsyncSession, yandex_id: str):
    result = await db.execute(select(User).filter(User.yandex_id == yandex_id))
    return result.scalars().first()

async def create_or_update_user(db: AsyncSession, user_data: dict):
    user = await get_user_by_yandex_id(db, user_data["yandex_id"])
    
    if user:
        user.access_token = user_data["access_token"]
        user.refresh_token = user_data["refresh_token"]
    else:
        user = User(**user_data)
        db.add(user)
    
    await db.commit()
    return user
