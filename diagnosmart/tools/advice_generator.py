"""Tool for generating safe, human-readable preliminary medical guidance."""

from __future__ import annotations

from diagnosmart.config import LOG_PATH, MEDICAL_DISCLAIMER
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)


def generate_advice(conditions: list[str]) -> str:
    """Generate concise, non-diagnostic advice from likely conditions.

    Args:
        conditions: Ranked list of possible conditions.

    Returns:
        str: Human-readable advice including mandatory safety disclaimer.

    Raises:
        ValueError: If conditions is not a list.
    """
    if not isinstance(conditions, list):
        raise ValueError("Conditions must be provided as a list of strings.")

    cleaned_conditions = [c.strip() for c in conditions if isinstance(c, str) and c.strip()]

    if not cleaned_conditions or cleaned_conditions == ["Insufficient symptom data"]:
        advice = (
            "The provided information is not enough to suggest likely conditions. "
            "Track your symptoms and consult a qualified doctor if symptoms continue. "
            f"{MEDICAL_DISCLAIMER}"
        )
    else:
        joined = ", ".join(cleaned_conditions)
        advice = (
            f"Based on the symptom pattern, possible related conditions include: {joined}. "
            "Please rest, stay hydrated, monitor symptom progression, and seek professional care "
            "if symptoms worsen or persist. "
            f"{MEDICAL_DISCLAIMER}"
        )

    log_event(
        LOGGER,
        event="tool_output",
        message="Advice generator produced safety-focused guidance.",
        meta={"tool": "generate_advice", "input": cleaned_conditions, "output": advice},
    )
    return advice
