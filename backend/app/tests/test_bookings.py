import asyncio

import pytest
from conftest import auth_header, create_test_user, login_user
from httpx import AsyncClient


@pytest.mark.anyio
async def create_double_bookings(client: AsyncClient):
    