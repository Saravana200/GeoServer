from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:test%40123@127.0.0.1:5432/satfarm"
engine = create_async_engine(DATABASE_URL, echo=True)

session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit= False,
)

async def async_session():
    async with session_maker() as session:
        yield session



