import asyncio
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from models import Booking, Payment, Premise, User  # adjust to your models path
from services.bookings_service import BookingService
from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from tests.helpers import auth_header

PREMISE_JSON = {
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
    "features": {"floor": 3, "area": 45.5, "rooms": 2, "price": 10000},
}


@dataclass
class Ctx:
    landlord_id: int
    renter_id: int
    premise_id: int
    landlord_headers: dict[str, str]
    renter_headers: dict[str, str]


async def _register_and_login(
    client: AsyncClient, username: str, email: str, contact_number: str
) -> dict[str, str]:
    """Register a user and return auth headers for them."""
    password = "123456789"
    reg = await client.post(
        "/api/users/auth/sign-up",
        json={
            "username": username,
            "email": email,
            "password": password,
            "contact_number": contact_number,
        },
    )
    assert reg.status_code in (200, 201), reg.text
    login = await client.post(
        "/api/users/auth/sign-in", data={"username": email, "password": password}
    )
    assert login.status_code == 200, login.text
    return auth_header(login.json()["access_token"])


async def _setup(
    client: AsyncClient, db: AsyncSession, renter_balance: str = "50000"
) -> Ctx:
    """Create a landlord with a premise (10 000 per night) and a funded renter."""
    landlord_headers = await _register_and_login(
        client, "landlord", "landlord@mail.com", "87770001122"
    )
    renter_headers = await _register_and_login(
        client, "renter", "renter@mail.com", "87770001133"
    )
    resp = await client.post(
        "/api/premises/new", json=PREMISE_JSON, headers=landlord_headers
    )
    assert resp.status_code in (200, 201), resp.text

    landlord_id = await db.scalar(
        select(User.id).where(User.email == "landlord@mail.com")
    )
    renter_id = await db.scalar(select(User.id).where(User.email == "renter@mail.com"))
    premise_id = await db.scalar(select(Premise.id))

    # Fund the renter directly in the DB so the tests don't depend on /top-up.
    await db.execute(
        update(User).where(User.id == renter_id).values(balance=Decimal(renter_balance))
    )
    await db.commit()
    return Ctx(landlord_id, renter_id, premise_id, landlord_headers, renter_headers)


async def _book(client: AsyncClient, ctx: Ctx, date_from: date, date_to: date):
    return await client.post(
        "/api/bookings",
        json={
            "premise_id": ctx.premise_id,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
        },
        headers=ctx.renter_headers,
    )


async def _balance(db: AsyncSession, user_id: int) -> Decimal:
    # Selecting a column (not the ORM object) always returns the fresh DB value.
    return await db.scalar(select(User.balance).where(User.id == user_id))


@pytest.mark.anyio
async def test_create_double_bookings(concurrent_client: AsyncClient):
    landlord = await _register_and_login(
        concurrent_client, "landlord", "landlord@mail.com", "87770001122"
    )
    renter_1 = await _register_and_login(
        concurrent_client, "renter1", "renter1@mail.com", "87770001133"
    )
    renter_2 = await _register_and_login(
        concurrent_client, "renter2", "renter2@mail.com", "87770001144"
    )

    # Users get ids 1, 2, 3 in registration order (the DB is reset between tests).
    for user_id, headers in ((2, renter_1), (3, renter_2)):
        top_up = await concurrent_client.post(
            f"/api/users/{user_id}/top-up", json={"sum": 50000}, headers=headers
        )
        assert top_up.status_code in (200, 201), top_up.text

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
        headers=landlord,
    )
    assert premise_response.status_code in (200, 201), premise_response.text
    print("PREMISE RESPONSE:", premise_response.json())
    premise_id = 1

    today = date.today()
    payload = {
        "premise_id": premise_id,
        "date_from": (today + timedelta(days=10)).isoformat(),
        "date_to": (today + timedelta(days=12)).isoformat(),
    }

    responses = await asyncio.gather(
        concurrent_client.post("/api/bookings", json=payload, headers=renter_1),
        concurrent_client.post("/api/bookings", json=payload, headers=renter_2),
    )

    statuses = [r.status_code for r in responses]
    print("statuses:", statuses, [r.text for r in responses])

    assert statuses.count(201) == 1


@pytest.mark.anyio
async def test_cancel_before_arrival_refunds_renter(client, db_session):
    """Cancelling before the check-in day returns the full amount to the renter."""
    ctx = await _setup(client, db_session)
    today = date.today()

    resp = await _book(
        client, ctx, today + timedelta(days=1), today + timedelta(days=3)
    )
    assert resp.status_code == 201, resp.text
    assert await _balance(db_session, ctx.renter_id) == Decimal("30000")  # 2 nights

    booking_id = await db_session.scalar(select(Booking.id))
    cancel = await client.post(
        f"/api/bookings/{booking_id}/cancel", headers=ctx.renter_headers
    )
    assert cancel.status_code == 200, cancel.text

    assert await _balance(db_session, ctx.renter_id) == Decimal("50000")
    assert await _balance(db_session, ctx.landlord_id) == Decimal("0")
    assert await db_session.scalar(select(Payment.status)) == "refunded"
    assert await db_session.scalar(select(Booking.status)) == "cancelled"


@pytest.mark.anyio
async def test_cancel_on_arrival_day_pays_landlord(client, db_session):
    """Cancelling on the check-in day: no refund, landlord gets total minus 5%."""
    ctx = await _setup(client, db_session)
    today = date.today()

    resp = await _book(client, ctx, today, today + timedelta(days=2))
    assert resp.status_code == 201, resp.text

    booking_id = await db_session.scalar(select(Booking.id))
    cancel = await client.post(
        f"/api/bookings/{booking_id}/cancel", headers=ctx.renter_headers
    )
    assert cancel.status_code == 200, cancel.text

    assert await _balance(db_session, ctx.renter_id) == Decimal("30000")  # no refund
    assert await _balance(db_session, ctx.landlord_id) == Decimal("19000")  # 20000 - 5%
    assert await db_session.scalar(select(Payment.status)) == "released"
    assert await db_session.scalar(select(Booking.status)) == "cancelled"


@pytest.mark.anyio
async def test_second_cancel_does_not_refund_twice(client, db_session):
    """A repeated cancel request must not move money a second time."""
    ctx = await _setup(client, db_session)
    today = date.today()
    await _book(client, ctx, today + timedelta(days=1), today + timedelta(days=3))
    booking_id = await db_session.scalar(select(Booking.id))
    url = f"/api/bookings/{booking_id}/cancel"

    first = await client.post(url, headers=ctx.renter_headers)
    assert first.status_code == 200, first.text

    second = await client.post(url, headers=ctx.renter_headers)
    assert second.status_code >= 400  # tighten to 409 once you return it

    assert await _balance(db_session, ctx.renter_id) == Decimal("50000")  # not 70000


@pytest.mark.anyio
async def test_insufficient_funds_leaves_everything_unchanged(client, db_session):
    """Not enough money: no booking, no payment, balance untouched."""
    ctx = await _setup(client, db_session, renter_balance="1000")
    today = date.today()

    resp = await _book(
        client, ctx, today + timedelta(days=1), today + timedelta(days=3)
    )
    assert resp.status_code >= 400
    assert resp.status_code != 201

    assert await _balance(db_session, ctx.renter_id) == Decimal("1000")
    assert await db_session.scalar(select(func.count()).select_from(Booking)) == 0
    assert await db_session.scalar(select(func.count()).select_from(Payment)) == 0


@pytest.mark.anyio
async def test_cannot_cancel_someone_elses_booking(client, db_session):
    """Another user gets 404 and nothing changes."""
    ctx = await _setup(client, db_session)
    today = date.today()
    await _book(client, ctx, today + timedelta(days=1), today + timedelta(days=3))
    booking_id = await db_session.scalar(select(Booking.id))

    stranger = await _register_and_login(
        client, "stranger", "stranger@mail.com", "87770001144"
    )
    resp = await client.post(f"/api/bookings/{booking_id}/cancel", headers=stranger)
    assert resp.status_code == 404

    assert await db_session.scalar(select(Booking.status)) == "confirmed"
    assert await db_session.scalar(select(Payment.status)) == "frozen"


async def _create_finished_booking(client, db: AsyncSession, ctx: Ctx) -> int:
    """Create a booking via the API, then move its dates into the past."""
    today = date.today()
    resp = await _book(
        client, ctx, today + timedelta(days=1), today + timedelta(days=3)
    )
    assert resp.status_code == 201, resp.text
    booking_id = await db.scalar(select(Booking.id))

    # The API rejects past dates, so shift the stay into the past directly in the DB.
    await db.execute(
        text(
            "UPDATE bookings "
            "SET during = daterange(CAST(:d_from AS date), CAST(:d_to AS date), '[)') "
            "WHERE id = :id"
        ),
        {
            "d_from": today - timedelta(days=3),
            "d_to": today - timedelta(days=1),
            "id": booking_id,
        },
    )
    await db.commit()
    return booking_id


@pytest.mark.anyio
async def test_complete_booking_pays_landlord_minus_commission(client, db_session):
    """A finished booking is completed and the landlord gets total minus 5%."""
    ctx = await _setup(client, db_session)
    booking_id = await _create_finished_booking(client, db_session, ctx)
    service = BookingService(db_session)

    # The scheduler job would pick this booking up.
    finished = await service.booking_repo.get_finished_booking_ids(date.today())
    assert finished == [booking_id]

    await service.complete_booking_and_payment(booking_id)

    assert await _balance(db_session, ctx.landlord_id) == Decimal("19000")  # 20000 - 5%
    assert await _balance(db_session, ctx.renter_id) == Decimal("30000")  # unchanged
    assert await db_session.scalar(select(Payment.status)) == "released"
    assert await db_session.scalar(select(Booking.status)) == "completed"


@pytest.mark.anyio
async def test_complete_booking_twice_does_not_pay_twice(client, db_session):
    """Running the payout again must not credit the landlord a second time."""
    ctx = await _setup(client, db_session)
    booking_id = await _create_finished_booking(client, db_session, ctx)
    service = BookingService(db_session)

    await service.complete_booking_and_payment(booking_id)
    try:
        await service.complete_booking_and_payment(booking_id)
    except HTTPException:
        pass  # a rejected repeat is fine; paying twice is not

    assert await _balance(db_session, ctx.landlord_id) == Decimal("19000")  # not 38000
