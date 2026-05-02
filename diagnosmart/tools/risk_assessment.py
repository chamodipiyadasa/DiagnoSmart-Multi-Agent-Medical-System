"""Tool for assigning risk levels based on symptom criticality."""

from __future__ import annotations

from diagnosmart.config import LOG_PATH
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)

HIGH_RISK_SIGNS: set[str] = {
    "chest pain",
    "shortness of breath",
    "severe headache",
    "high fever",
    "confusion",
    "fainting",
}

MEDIUM_RISK_SIGNS: set[str] = {
    "fever",
    "vomiting",
    "persistent cough",
    "joint pain",
    "rash",
    "abdominal pain",
}


def assess_risk(symptoms: list[str]) -> str:
    """Assess risk level as LOW, MEDIUM, or HIGH from symptom list.

    Args:
        symptoms: List of symptom strings.

    Returns:
        str: Risk classification label.

    Raises:
        ValueError: If symptoms input is invalid.
    """
    if not isinstance(symptoms, list):
        raise ValueError("Symptoms must be a list of strings.")

    normalized = {s.lower().strip() for s in symptoms if isinstance(s, str) and s.strip()}

    if normalized & HIGH_RISK_SIGNS:
        level = "HIGH"
    elif normalized & MEDIUM_RISK_SIGNS:
        level = "MEDIUM"
    else:
        level = "LOW"

    log_event(
        LOGGER,
        event="tool_output",
        message="Risk assessment completed.",
        meta={"tool": "assess_risk", "input": sorted(normalized), "output": level},
    )
    return level
