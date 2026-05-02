"""Global shared state passed across all LangGraph nodes."""

from __future__ import annotations

from typing import TypedDict


class GlobalState(TypedDict):
    """State object for the full diagnosis pipeline."""

    user_input: str
    symptoms: list[str]
    duration: str
    severity: str
    conditions: list[str]
    advice: str
    risk_level: str


def create_initial_state(user_input: str) -> GlobalState:
    """Create the initial state for a new workflow run.

    Args:
        user_input: Free-text symptom description from user.

    Returns:
        GlobalState: Zero-initialized workflow state with user input attached.
    """
    return GlobalState(
        user_input=user_input,
        symptoms=[],
        duration="",
        severity="",
        conditions=[],
        advice="",
        risk_level="",
    )
