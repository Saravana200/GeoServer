from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

class UserService:

    def __init__(self, _session: AsyncSession):
        self.session=_session

    async def get_user(self,user_name:str)->User:
        query = select(User).where(User.name == user_name)
        user = await self.session.execute(query)
        return user.scalar_one_or_none()
    
    async def add_user(self, user:User)->User:
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            print(f"failed to save due to :{e}")
            raise
