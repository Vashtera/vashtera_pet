import asyncio

import pytest
from httpx import AsyncClient

from .conftest import auth_header


async def register_and_login(
    client: AsyncClient, username: str, email: str, contact_number: str
) -> dict[str, str]:
    password = "123456789"
    reg = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
            "contact_number": contact_number,
        },
    )
    assert reg.status_code in (200, 201), reg.text

    login = await client.post(
        "/api/users/token",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200, login.text
    return auth_header(login.json()["access_token"])


@pytest.mark.anyio
async def test_create_double_bookings(concurrent_client: AsyncClient):
    headers_1 = await register_and_login(
        concurrent_client, "testuser1", "testemail1@mail.com", "87770001122"
    )
    headers_2 = await register_and_login(
        concurrent_client, "testuser2", "testemail2@mail.com", "87770001133"
    )

    premise_response = await concurrent_client.post(
        "/api/premises/new",
        json={
            "premise_data": {
                "premise_type": "apartments",
                "description": "Test apartment",
                "contact_number": "87770001122",
            },
            "address": {
                "street": "Test street",
                "city": "Aktobe",
                "district": "Test district",
                "house_number": 1,
            },
            "features": {
                "floor": 3,
                "area": 45.5,
                "rooms": 2,
                "price": 10000,
            },
        },
        headers=headers_1,
    )
    assert premise_response.status_code in (200, 201), premise_response.text
    print("PREMISE RESPONSE:", premise_response.json())
    premise_id = 1

    payload = {
        "premise_id": premise_id,
        "date_from": "2026-11-10",
        "date_to": "2026-11-12",
    }

    responses = await asyncio.gather(
        concurrent_client.post("/api/bookings", json=payload, headers=headers_1),
        concurrent_client.post("/api/bookings", json=payload, headers=headers_2),
    )

    statuses = [r.status_code for r in responses]
    print("statuses:", statuses, [r.text for r in responses])

    assert statuses.count(201) == 1
