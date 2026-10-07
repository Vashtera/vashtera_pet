from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users_model import User


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int):
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_email(self, users_email: str):
        stmt = select(User).where(User.email == users_email)
        result = await self.session.execute(stmt)
        return result.scalars().first()
