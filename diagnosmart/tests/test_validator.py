"""Tests for Risk Validator Agent."""

from diagnosmart.agents.risk_validator import run_risk_validator
from diagnosmart.state.global_state import create_initial_state


def test_validator_detects_high_risk() -> None:
    state = create_initial_state("chest pain and shortness of breath")
    state["symptoms"] = ["chest pain", "shortness of breath"]

    updated = run_risk_validator(state, llm=None)
    assert updated["risk_level"] == "HIGH"


def test_validator_detects_medium_risk() -> None:
    state = create_initial_state("fever and rash")
    state["symptoms"] = ["fever", "rash"]

    updated = run_risk_validator(state, llm=None)
    assert updated["risk_level"] == "MEDIUM"


def test_validator_edge_case_low_risk() -> None:
    state = create_initial_state("mild sneezing")
    state["symptoms"] = ["sneezing"]

    updated = run_risk_validator(state, llm=None)
    assert updated["risk_level"] == "LOW"
