"""Tool for parsing free-text symptoms into structured medical context."""

from __future__ import annotations

import re
from typing import Any

from diagnosmart.config import LOG_PATH
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)

KNOWN_SYMPTOMS: set[str] = {
    "fever",
    "high fever",
    "headache",
    "body ache",
    "fatigue",
    "cough",
    "dry cough",
    "sore throat",
    "runny nose",
    "sneezing",
    "shortness of breath",
    "wheezing",
    "chest pain",
    "chest tightness",
    "rash",
    "nausea",
    "vomiting",
    "abdominal pain",
    "bloating",
    "loss of taste",
    "loss of smell",
    "joint pain",
    "dizziness",
}

SEVERITY_KEYWORDS: dict[str, list[str]] = {
    "high": ["severe", "intense", "unbearable", "worst", "extreme"],
    "moderate": ["moderate", "persistent", "ongoing"],
    "low": ["mild", "slight", "light"],
}


def _extract_duration(text: str) -> str:
    duration_pattern = re.compile(
        r"(\b\d+\s*(?:hour|hours|day|days|week|weeks)\b|\bsince\s+yesterday\b)",
        flags=re.IGNORECASE,
    )
    match = duration_pattern.search(text)
    return match.group(0).lower() if match else "unknown"


def _extract_severity(text: str) -> str:
    lowered = text.lower()
    for level, keywords in SEVERITY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return level

    if "high fever" in lowered or "chest pain" in lowered or "shortness of breath" in lowered:
        return "high"
    return "moderate"


def extract_symptoms(text: str) -> dict[str, Any]:
    """Extract symptoms, duration, and severity from raw user text.

    Args:
        text: User-provided free-text symptom description.

    Returns:
        dict[str, Any]: Parsed structure with keys: symptoms, duration, severity.

    Raises:
        ValueError: If input text is empty or invalid.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input symptom text must be a non-empty string.")

    lowered = text.lower()
    matched = [symptom for symptom in KNOWN_SYMPTOMS if symptom in lowered]

    parsed: dict[str, Any] = {
        "symptoms": sorted(set(matched)),
        "duration": _extract_duration(text),
        "severity": _extract_severity(text),
    }

    log_event(
        LOGGER,
        event="tool_output",
        message="Symptom parser extracted structured data.",
        meta={"tool": "extract_symptoms", "input": text, "output": parsed},
    )
    return parsed
