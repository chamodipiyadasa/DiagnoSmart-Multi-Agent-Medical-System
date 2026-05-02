"""Risk Validator Agent: classifies user risk level from symptom profile."""

from __future__ import annotations

from typing import Any

from diagnosmart.config import LOG_PATH
from diagnosmart.state.global_state import GlobalState
from diagnosmart.tools.risk_assessment import assess_risk
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)

SYSTEM_PROMPT = (
    "You are Risk Validator Agent. Detect red-flag symptom patterns and classify risk "
    "as LOW, MEDIUM, or HIGH. Prioritize patient safety over optimism."
)


def run_risk_validator(state: GlobalState, llm: Any | None = None) -> GlobalState:
    """Assess final risk level and update global state.

    Args:
        state: Current workflow state.
        llm: Optional local LLM client.

    Returns:
        GlobalState: Updated state containing risk classification.
    """
    symptoms = state.get("symptoms", [])
    log_event(
        LOGGER,
        event="agent_start",
        message="Risk Validator Agent started.",
        meta={"agent": "RiskValidator", "input": symptoms},
    )

    try:
        risk_level = assess_risk(symptoms)
    except Exception as exc:
        log_event(
            LOGGER,
            event="agent_error",
            message="Risk Validator tool execution failed.",
            meta={"agent": "RiskValidator", "error": str(exc)},
        )
        risk_level = "MEDIUM"

    if llm is not None:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Symptoms: {symptoms}\n"
            f"Tool risk level: {risk_level}\n"
            "Return one short justification sentence only."
        )
        try:
            llm_response = llm.invoke(prompt)
            note = getattr(llm_response, "content", str(llm_response))
            log_event(
                LOGGER,
                event="agent_reasoning",
                message="Risk Validator generated justification note.",
                meta={"agent": "RiskValidator", "llm_note": str(note)},
            )
        except Exception as exc:
            log_event(
                LOGGER,
                event="agent_error",
                message="Risk Validator LLM call failed.",
                meta={"agent": "RiskValidator", "error": str(exc)},
            )

    state["risk_level"] = risk_level

    log_event(
        LOGGER,
        event="agent_output",
        message="Risk Validator Agent completed.",
        meta={"agent": "RiskValidator", "output": risk_level},
    )
    return state
