"""Structured contextual logging."""
import logging
import json
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("operation", "project_id", "question_id", "expert_id",
                     "transcript_id", "duration_ms", "status", "error", "detail"):
            value = getattr(record, key, None)
            if value is not None:
                log_data[key] = value

        return json.dumps(log_data, default=str)


def setup_logging(debug: bool = False) -> None:
    """Configure structured logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger("insightos")
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger under the insightos namespace."""
    return logging.getLogger(f"insightos.{name}")
