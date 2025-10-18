import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def _configure_handler(handler: logging.Handler) -> logging.Handler:
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return handler


def setup_logger(name: Optional[str] = "backend") -> logging.Logger:
    """Configure console + rotating file logging shared across the backend."""
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    file_handler = RotatingFileHandler(
        log_dir / "backend.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    console_handler = logging.StreamHandler()

    logger.setLevel(logging.INFO)
    logger.addHandler(_configure_handler(file_handler))
    logger.addHandler(_configure_handler(console_handler))
    logger.propagate = False

    shared_handlers = logger.handlers.copy()

    # Align Uvicorn loggers so everything lands in the same log targets.
    for uv_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(uv_logger_name)
        uv_logger.setLevel(logging.INFO)
        uv_logger.handlers = []
        for handler in shared_handlers:
            uv_logger.addHandler(handler)
        uv_logger.propagate = False

    # Ensure third-party loggers fall back to our configuration.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in shared_handlers:
        if handler not in root_logger.handlers:
            root_logger.addHandler(handler)

    return logger
