"""Medical Research Agent: maps symptoms to possible conditions via local lookup."""

from __future__ import annotations

from typing import Any

from diagnosmart.config import LOG_PATH
from diagnosmart.state.global_state import GlobalState
from diagnosmart.tools.disease_lookup import find_conditions
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)

SYSTEM_PROMPT = (
    "You are Medical Research Agent. Use only provided symptom evidence and local data results. "
    "Rank likely conditions conservatively and avoid definitive diagnosis claims."
)


def run_medical_research(state: GlobalState, llm: Any | None = None) -> GlobalState:
    """Run symptom-to-condition research and update global state.

    Args:
        state: Current workflow state.
        llm: Optional local LLM client.

    Returns:
        GlobalState: Updated state containing likely conditions.
    """
    symptoms = state.get("symptoms", [])
    log_event(
        LOGGER,
        event="agent_start",
        message="Medical Research Agent started.",
        meta={"agent": "MedicalResearch", "input": symptoms},
    )

    try:
        conditions = find_conditions(symptoms)
    except Exception as exc:
        log_event(
            LOGGER,
            event="agent_error",
            message="Medical Research Agent lookup failed.",
            meta={"agent": "MedicalResearch", "error": str(exc)},
        )
        conditions = ["No strong match found"]

    if llm is not None:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Symptoms: {symptoms}\n"
            f"Tool conditions: {conditions}\n"
            "Return one short line explaining why these conditions are plausible."
        )
        try:
            llm_response = llm.invoke(prompt)
            rationale = getattr(llm_response, "content", str(llm_response))
            log_event(
                LOGGER,
                event="agent_reasoning",
                message="Medical Research Agent rationale generated.",
                meta={"agent": "MedicalResearch", "llm_note": str(rationale)},
            )
        except Exception as exc:
            log_event(
                LOGGER,
                event="agent_error",
                message="Medical Research Agent LLM call failed.",
                meta={"agent": "MedicalResearch", "error": str(exc)},
            )

    state["conditions"] = conditions

    log_event(
        LOGGER,
        event="agent_output",
        message="Medical Research Agent completed.",
        meta={"agent": "MedicalResearch", "output": conditions},
    )
    return state
