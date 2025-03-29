import asyncio
from app.database import Base, engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Run the async function
asyncio.run(create_tables())
