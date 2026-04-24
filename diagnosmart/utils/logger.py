"""Structured logging utilities for observability across agents and tools."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonFormatter(logging.Formatter):
    """Formats log records as compact JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "event"):
            payload["event"] = record.event
        if hasattr(record, "meta"):
            payload["meta"] = record.meta
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


class TimelineFormatter(logging.Formatter):
    """Formats records into a concise human-readable timeline for terminal output."""

    EVENT_LABELS = {
        "agent_start": "START",
        "tool_output": "TOOL",
        "agent_output": "DONE",
        "agent_error": "ERROR",
    }
    EVENT_COLORS = {
        "agent_start": "\033[36m",  # cyan
        "tool_output": "\033[35m",  # magenta
        "agent_output": "\033[32m",  # green
        "agent_error": "\033[31m",  # red
    }
    RESET = "\033[0m"

    def __init__(self) -> None:
        super().__init__()
        self._use_color = self._supports_color()

    def _supports_color(self) -> bool:
        """Enable ANSI only when running in a capable terminal."""
        if os.getenv("NO_COLOR"):
            return False
        term = os.getenv("TERM", "")
        if term.lower() == "dumb":
            return False
        return sys.stderr.isatty()

    def _shorten(self, value: Any, max_len: int = 120) -> str:
        text = str(value).replace("\n", " ").strip()
        if len(text) <= max_len:
            return text
        return f"{text[: max_len - 3]}..."

    def _extract_subject(self, meta: dict[str, Any]) -> str:
        if not isinstance(meta, dict):
            return ""
        if "agent" in meta:
            return self._shorten(meta["agent"], max_len=48)
        if "tool" in meta:
            return self._shorten(meta["tool"], max_len=48)
        return ""

    def _extract_detail(self, meta: dict[str, Any], event: str, message: str) -> str:
        if not isinstance(meta, dict):
            return self._shorten(message)
        if event == "agent_start":
            detail = meta.get("input", "")
        elif event in {"tool_output", "agent_output"}:
            detail = meta.get("output", meta.get("llm_note", meta.get("llm_output", "")))
        elif event == "agent_error":
            detail = meta.get("error", message)
        else:
            detail = message
        return self._shorten(detail)

    def format(self, record: logging.LogRecord) -> str:
        event = str(getattr(record, "event", "log"))
        label = self.EVENT_LABELS.get(event, event.upper())
        meta = getattr(record, "meta", {})
        subject = self._extract_subject(meta if isinstance(meta, dict) else {})
        detail = self._extract_detail(meta if isinstance(meta, dict) else {}, event, record.getMessage())

        time = datetime.now().strftime("%H:%M:%S")
        label_text = f"[{label}]"
        if self._use_color:
            color = self.EVENT_COLORS.get(event, "")
            if color:
                label_text = f"{color}{label_text}{self.RESET}"

        parts = [time, label_text]
        if subject:
            parts.append(subject)
        if detail:
            parts.append(f"- {detail}")
        return " ".join(parts)


def setup_logger(log_path: Path) -> logging.Logger:
    """Configure and return the application logger.

    Args:
        log_path: File path where logs should be stored.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("diagnosmart")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_formatter = JsonFormatter()
    console_formatter = TimelineFormatter()

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(file_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def log_event(logger: logging.Logger, event: str, message: str, meta: dict[str, Any]) -> None:
    """Emit a structured event log.

    Args:
        logger: Logger instance.
        event: Event name (e.g., agent_start, tool_output).
        message: Human-readable summary.
        meta: Structured metadata for observability.
    """
    logger.info(message, extra={"event": event, "meta": meta})
