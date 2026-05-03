"""Tests for Medical Research Agent."""

from diagnosmart.agents.medical_research import run_medical_research
from diagnosmart.state.global_state import create_initial_state


def test_research_returns_relevant_conditions() -> None:
    state = create_initial_state("fever and cough")
    state["symptoms"] = ["fever", "cough", "fatigue"]

    updated = run_medical_research(state, llm=None)
    assert len(updated["conditions"]) >= 1
    assert any("Flu" in condition or "COVID" in condition for condition in updated["conditions"])


def test_research_handles_single_symptom() -> None:
    state = create_initial_state("headache")
    state["symptoms"] = ["headache"]

    updated = run_medical_research(state, llm=None)
    assert isinstance(updated["conditions"], list)
    assert len(updated["conditions"]) >= 1


def test_research_edge_case_no_symptoms() -> None:
    state = create_initial_state("no symptoms")
    state["symptoms"] = []

    updated = run_medical_research(state, llm=None)
    assert updated["conditions"] == ["Insufficient symptom data"]
