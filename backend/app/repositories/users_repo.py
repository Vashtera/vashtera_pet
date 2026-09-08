from typing import Optional

from app.models.users_model import User
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int):
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
