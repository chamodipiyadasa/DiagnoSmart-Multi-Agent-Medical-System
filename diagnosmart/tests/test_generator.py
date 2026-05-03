"""Tests for Diagnosis Generator Agent."""

from diagnosmart.agents.diagnosis_generator import run_diagnosis_generator
from diagnosmart.config import MEDICAL_DISCLAIMER
from diagnosmart.state.global_state import create_initial_state


def test_generator_creates_advice_with_disclaimer() -> None:
    state = create_initial_state("fever and cough")
    state["conditions"] = ["Influenza (Flu)", "COVID-19"]

    updated = run_diagnosis_generator(state, llm=None)
    assert "possible related conditions" in updated["advice"].lower()
    assert MEDICAL_DISCLAIMER in updated["advice"]


def test_generator_handles_single_condition() -> None:
    state = create_initial_state("headache")
    state["conditions"] = ["Migraine"]

    updated = run_diagnosis_generator(state, llm=None)
    assert "Migraine" in updated["advice"]


def test_generator_edge_case_insufficient_data() -> None:
    state = create_initial_state("")
    state["conditions"] = ["Insufficient symptom data"]

    updated = run_diagnosis_generator(state, llm=None)
    assert "not enough" in updated["advice"].lower() or "insufficient" in updated["advice"].lower()
    assert MEDICAL_DISCLAIMER in updated["advice"]
