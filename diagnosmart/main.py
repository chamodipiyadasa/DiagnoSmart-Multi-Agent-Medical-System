"""Entry point for running the DiagnoSmart multi-agent workflow locally."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure package imports work when running `python main.py` from this directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_ollama import ChatOllama

from diagnosmart.config import LOG_PATH, OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE
from diagnosmart.orchestration.workflow import build_workflow
from diagnosmart.state.global_state import create_initial_state
from diagnosmart.utils.logger import log_event, setup_logger

LOGGER = setup_logger(LOG_PATH)


def init_llm() -> ChatOllama | None:
    """Initialize local Ollama-backed LLM client.

    Returns:
        ChatOllama | None: Ready local LLM client if available, otherwise None.
    """
    try:
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            temperature=OLLAMA_TEMPERATURE,
            base_url=OLLAMA_BASE_URL,
            client_kwargs={"trust_env": False},
        )
        log_event(
            LOGGER,
            event="startup",
            message="Ollama client initialized.",
            meta={"model": OLLAMA_MODEL, "base_url": OLLAMA_BASE_URL},
        )
        return llm
    except Exception as exc:
        log_event(
            LOGGER,
            event="startup_warning",
            message="Ollama initialization failed. Running in tool-only mode.",
            meta={"error": str(exc)},
        )
        return None


def run_diagnosmart(user_input: str) -> dict:
    """Execute the full LangGraph workflow for a user symptom description.

    Args:
        user_input: Raw symptom text from user.

    Returns:
        dict: Final structured output with symptoms, conditions, advice, and risk level.
    """
    llm = init_llm()
    workflow = build_workflow(llm=llm)

    initial_state = create_initial_state(user_input=user_input)
    final_state = workflow.invoke(initial_state)

    return {
        "symptoms": final_state.get("symptoms", []),
        "conditions": final_state.get("conditions", []),
        "advice": final_state.get("advice", ""),
        "risk_level": final_state.get("risk_level", ""),
    }


if __name__ == "__main__":
    # Example input and output demonstration for assignment requirements.
    example_input = "I have fever, headache, and body ache for 2 days with moderate pain."
    print("Input:")
    print(example_input)
    print("\nOutput:")
    output = run_diagnosmart(example_input)
    print(json.dumps(output, indent=2))
