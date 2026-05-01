"""Diagnosis Generator Agent: creates safe human-readable preliminary guidance."""

from __future__ import annotations

from typing import Any

from diagnosmart.config import LOG_PATH, MEDICAL_DISCLAIMER
from diagnosmart.state.global_state import GlobalState
from diagnosmart.tools.advice_generator import generate_advice
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)

SYSTEM_PROMPT = (
    "You are Diagnosis Generator Agent. Convert condition candidates into clear, empathetic, "
    "and safety-first guidance. Never claim certainty. Always include the medical disclaimer."
)


def run_diagnosis_generator(state: GlobalState, llm: Any | None = None) -> GlobalState:
    """Generate non-diagnostic user advice and update global state.

    Args:
        state: Current workflow state.
        llm: Optional local LLM client.

    Returns:
        GlobalState: Updated state containing advice text.
    """
    conditions = state.get("conditions", [])
    log_event(
        LOGGER,
        event="agent_start",
        message="Diagnosis Generator Agent started.",
        meta={"agent": "DiagnosisGenerator", "input": conditions},
    )

    try:
        advice = generate_advice(conditions)
    except Exception as exc:
        log_event(
            LOGGER,
            event="agent_error",
            message="Diagnosis Generator tool execution failed.",
            meta={"agent": "DiagnosisGenerator", "error": str(exc)},
        )
        advice = f"Unable to generate advice safely. {MEDICAL_DISCLAIMER}"

    if llm is not None:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Conditions: {conditions}\n"
            f"Tool advice draft: {advice}\n"
            "Return a polished 2-3 sentence version that keeps disclaimer unchanged."
        )
        try:
            llm_response = llm.invoke(prompt)
            llm_advice = str(getattr(llm_response, "content", str(llm_response))).strip()
            if MEDICAL_DISCLAIMER not in llm_advice:
                llm_advice = f"{llm_advice} {MEDICAL_DISCLAIMER}".strip()
            if llm_advice:
                advice = llm_advice
            log_event(
                LOGGER,
                event="agent_reasoning",
                message="Diagnosis Generator refined advice using LLM.",
                meta={"agent": "DiagnosisGenerator", "llm_output": advice},
            )
        except Exception as exc:
            log_event(
                LOGGER,
                event="agent_error",
                message="Diagnosis Generator LLM call failed.",
                meta={"agent": "DiagnosisGenerator", "error": str(exc)},
            )

    state["advice"] = advice

    log_event(
        LOGGER,
        event="agent_output",
        message="Diagnosis Generator Agent completed.",
        meta={"agent": "DiagnosisGenerator", "output": advice},
    )
    return state
