"""Application-wide logging configuration.

Call :func:`setup_logging` exactly once, at application startup (for example
in ``main.py``, before the FastAPI app is created). After that, every module
only needs to obtain its own logger and write to it::

    import logging

    logger = logging.getLogger(__name__)
    logger.info("Booking created: booking_id=%s", booking_id)

Modules never create handlers or formatters themselves. All records
propagate to the root logger configured here, which sends them to the
console and to a rotating log file.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "vashtera.log"


def setup_logging(level: str = "INFO") -> None:
    """Configure application-wide logging: console plus a rotating file.

    Every log record is written to two places at once:

    * the console (the terminal where the server is running);
    * the file ``logs/vashtera.log``. When it reaches 5 MB it is renamed
      to ``vashtera.log.1`` and a fresh file is started. Up to 3 archived
      files are kept, the oldest one is deleted. This prevents the log
      from growing without limit.

    Each line has the same format in both places::

      2026-11-10 13:20:01 | INFO     | app.services.bookings_service | Booking cancelled

    that is: time | level | name of the module that wrote it | message.

    The ``logs/`` directory is created automatically if it does not exist.

    Note:
        This function configures the *root* logger, so it affects every
        logger in the application, including those of third-party
        libraries. It should be called only once. ``logging.basicConfig``
        does nothing if the root logger already has handlers, so a second
        call will silently be ignored.

    Args:
        level: Minimum severity that will be recorded. Records below this
            level are discarded. One of ``"DEBUG"``, ``"INFO"``,
            ``"WARNING"``, ``"ERROR"``, ``"CRITICAL"``. Use ``"INFO"`` in
            normal operation and ``"DEBUG"`` only while investigating a
            problem. Ideally the value comes from the settings (``.env``)
            so it can be changed without editing code.

    Raises:
        ValueError: If ``level`` is not a valid logging level name.
    """
    # Make sure the target directory exists. RotatingFileHandler creates the
    # file itself, but it does not create missing directories.
    LOG_DIR.mkdir(exist_ok=True)

    # The template that defines how every log line looks.
    # %(levelname)-8s pads the level name to 8 characters so that columns
    # line up (INFO and WARNING start the next column at the same position).
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    # Handler no. 1: print records to the console (stderr by default).
    # A handler decides WHERE a record goes; the formatter attached to it
    # decides HOW the record looks.
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    # Handler no. 2: write records to a file with automatic rotation.
    #   maxBytes=5_000_000 -> rotate when the file reaches about 5 MB
    #   backupCount=3      -> keep 3 archived files (.log.1, .log.2, .log.3)
    #   encoding="utf-8"   -> store non-ASCII text correctly
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Connect everything to the root logger: set the minimum level and
    # attach both handlers. From now on any logger obtained via
    # logging.getLogger(__name__) passes its records here.
    logging.basicConfig(level=level, handlers=[console, file_handler])
