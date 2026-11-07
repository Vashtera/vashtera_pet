import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

scheduler = AsyncIOScheduler(
    timezone="Asia/Aqtobe",
    job_defaults={"coalesce": True, "max_instances": 1},
)

scheduler.add_job(..., "cron", hour=15, minute=0)
