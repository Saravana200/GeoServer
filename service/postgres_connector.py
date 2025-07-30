from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "postgresql+asyncpg://postgres:test%40123@db:5432/Satfarm"
engine = create_async_engine(DATABASE_URL, echo=True)

session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit= False,
)

async def async_session():
    async with session_maker() as session:
        yield session



