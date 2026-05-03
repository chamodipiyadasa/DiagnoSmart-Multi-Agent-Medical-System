"""Tool for mapping symptoms to likely conditions via local dataset lookup."""

from __future__ import annotations

import json
from pathlib import Path

from diagnosmart.config import DATA_PATH, LOG_PATH
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)


def _load_dataset(dataset_path: Path) -> dict:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at path: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if "conditions" not in payload or not isinstance(payload["conditions"], list):
        raise ValueError("Invalid diseases dataset format. Missing 'conditions' list.")

    return payload


def find_conditions(symptoms: list[str]) -> list[str]:
    """Find possible conditions using local symptom-to-disease mapping.

    Args:
        symptoms: List of normalized symptom labels.

    Returns:
        list[str]: Ranked list of possible medical conditions.

    Raises:
        ValueError: If symptoms list is invalid.
        FileNotFoundError: If local dataset file is missing.
    """
    if not isinstance(symptoms, list):
        raise ValueError("Symptoms must be provided as a list of strings.")

    normalized_symptoms = {s.lower().strip() for s in symptoms if isinstance(s, str) and s.strip()}
    if not normalized_symptoms:
        return ["Insufficient symptom data"]

    payload = _load_dataset(DATA_PATH)

    scored: list[tuple[str, int]] = []
    for item in payload["conditions"]:
        condition_name = str(item.get("name", "Unknown Condition"))
        condition_symptoms = {s.lower().strip() for s in item.get("symptoms", []) if isinstance(s, str)}
        overlap = len(normalized_symptoms & condition_symptoms)
        if overlap > 0:
            scored.append((condition_name, overlap))

    scored.sort(key=lambda entry: entry[1], reverse=True)
    conditions = [name for name, _ in scored[:3]] if scored else ["No strong match found"]

    log_event(
        LOGGER,
        event="tool_output",
        message="Disease lookup generated possible conditions.",
        meta={"tool": "find_conditions", "input": sorted(normalized_symptoms), "output": conditions},
    )
    return conditions
