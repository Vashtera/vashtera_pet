import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..database import AsyncSessionFactory
from ..repositories.bookings_repo import BookingRepo
from ..services.bookings_service import BookingService

logger = logging.getLogger(__name__)

KZ_TZ = ZoneInfo("Asia/Aqtobe")


async def process_finished_bookings() -> None:
    """Complete all confirmed bookings whose check-out date has passed.

    Runs as a background job (see the scheduler below). The work is split in two steps:

    1. In a short read-only session, collect the ids of bookings that are
       still ``confirmed`` and whose stay has ended.
    2. Complete every booking in its own session and transaction, so a
       failure on one booking never rolls back the others.

    The job is safe to run more than once: ``complete_booking_and_payment`` uses
    conditional updates (booking must be ``confirmed``, payment must be
    ``frozen``), so a repeated run skips bookings that were already processed
    and never pays out twice.
    """
    today = datetime.now(KZ_TZ).date()  # "today" in Kazakhstan time, not server time

    async with AsyncSessionFactory() as session:
        ids = await BookingRepo(session).get_finished_booking_ids(today)

    logger.info("Found %d finished bookings to complete", len(ids))

    for booking_id in ids:
        async with AsyncSessionFactory() as session:
            service = BookingService(session)
            try:
                await service.complete_booking_and_payment(
                    booking_id
                )  # commits internally
            except Exception:
                await session.rollback()
                logger.exception("Failed to complete booking %s", booking_id)


# In-process scheduler. Coroutine jobs run in the event loop of the app.
# coalesce=True: missed runs are merged into one;
# max_instances=1: two copies of the job never run at the same time.
scheduler = AsyncIOScheduler(
    timezone="Asia/Aqtobe",
    job_defaults={"coalesce": True, "max_instances": 1},
)

# Run every day at 15:00 (Asia/Aqtobe), after the usual check-out time.
scheduler.add_job(process_finished_bookings, "cron", hour=15, minute=0)
