from typing import Optional

from app.models.users_model import User
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
