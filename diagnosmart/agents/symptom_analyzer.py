"""Symptom Analyzer Agent: transforms raw user text into structured symptom state."""

from __future__ import annotations

from typing import Any

from diagnosmart.config import LOG_PATH
from diagnosmart.state.global_state import GlobalState
from diagnosmart.tools.symptom_parser import extract_symptoms
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)

SYSTEM_PROMPT = (
    "You are Symptom Analyzer Agent. Extract health symptoms, duration, and severity from text. "
    "Be precise, do not invent symptoms, and return medically neutral reasoning."
)


def run_symptom_analyzer(state: GlobalState, llm: Any | None = None) -> GlobalState:
    """Run symptom analysis and update global state.

    Args:
        state: Current workflow state.
        llm: Optional local LLM client (Ollama via LangChain).

    Returns:
        GlobalState: Updated state with symptoms, duration, and severity.
    """
    log_event(
        LOGGER,
        event="agent_start",
        message="Symptom Analyzer started.",
        meta={"agent": "SymptomAnalyzer", "input": state.get("user_input", "")},
    )

    user_text = state.get("user_input", "")

    try:
        parsed = extract_symptoms(user_text)
    except Exception as exc:
        log_event(
            LOGGER,
            event="agent_error",
            message="Symptom Analyzer failed during parsing.",
            meta={"agent": "SymptomAnalyzer", "error": str(exc)},
        )
        parsed = {"symptoms": [], "duration": "unknown", "severity": "unknown"}

    if llm is not None:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"User input: {user_text}\n"
            f"Tool extraction: {parsed}\n"
            "Return one short validation sentence only."
        )
        try:
            llm_response = llm.invoke(prompt)
            validation_note = getattr(llm_response, "content", str(llm_response))
            log_event(
                LOGGER,
                event="agent_reasoning",
                message="Symptom Analyzer reasoning generated.",
                meta={"agent": "SymptomAnalyzer", "llm_note": str(validation_note)},
            )
        except Exception as exc:
            log_event(
                LOGGER,
                event="agent_error",
                message="Symptom Analyzer LLM call failed.",
                meta={"agent": "SymptomAnalyzer", "error": str(exc)},
            )

    state["symptoms"] = parsed["symptoms"]
    state["duration"] = parsed["duration"]
    state["severity"] = parsed["severity"]

    log_event(
        LOGGER,
        event="agent_output",
        message="Symptom Analyzer completed.",
        meta={
            "agent": "SymptomAnalyzer",
            "output": {
                "symptoms": state["symptoms"],
                "duration": state["duration"],
                "severity": state["severity"],
            },
        },
    )
    return state
