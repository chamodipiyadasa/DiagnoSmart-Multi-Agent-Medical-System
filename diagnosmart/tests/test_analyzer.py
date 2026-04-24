"""Tests for Symptom Analyzer Agent."""

from diagnosmart.agents.symptom_analyzer import run_symptom_analyzer
from diagnosmart.state.global_state import create_initial_state


def test_analyzer_extracts_basic_symptoms() -> None:
    state = create_initial_state("I have fever and headache for 2 days with moderate discomfort")
    updated = run_symptom_analyzer(state, llm=None)

    assert "fever" in updated["symptoms"]
    assert "headache" in updated["symptoms"]
    assert updated["duration"] == "2 days"


def test_analyzer_detects_high_severity_signals() -> None:
    state = create_initial_state("I have severe chest pain and shortness of breath for 1 day")
    updated = run_symptom_analyzer(state, llm=None)

    assert updated["severity"] == "high"
    assert "chest pain" in updated["symptoms"]


def test_analyzer_edge_case_empty_input() -> None:
    state = create_initial_state("")
    updated = run_symptom_analyzer(state, llm=None)

    assert updated["symptoms"] == []
    assert updated["duration"] in {"unknown", ""}
