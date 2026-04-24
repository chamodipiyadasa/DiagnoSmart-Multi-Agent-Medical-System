"""Tests for JSON file logging and human-readable console timeline output."""

from __future__ import annotations

import io
import json
import logging

from diagnosmart.agents.symptom_analyzer import run_symptom_analyzer
from diagnosmart.orchestration.workflow import build_workflow
from diagnosmart.state.global_state import create_initial_state
from diagnosmart.utils.logger import JsonFormatter, TimelineFormatter


def _make_record(message: str, event: str, meta: dict[str, object]) -> logging.LogRecord:
    record = logging.LogRecord(
        name="diagnosmart",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )
    record.event = event
    record.meta = meta
    return record


def test_timeline_formatter_labels(monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    formatter = TimelineFormatter()

    start = formatter.format(_make_record("Symptom Analyzer started.", "agent_start", {"agent": "SymptomAnalyzer", "input": "fever"}))
    tool = formatter.format(_make_record("Tool output ready.", "tool_output", {"tool": "extract_symptoms", "output": {"symptoms": ["fever"]}}))
    done = formatter.format(_make_record("Agent completed.", "agent_output", {"agent": "SymptomAnalyzer", "output": {"symptoms": ["fever"]}}))
    error = formatter.format(_make_record("Agent failed.", "agent_error", {"agent": "SymptomAnalyzer", "error": "boom"}))

    assert "[START]" in start
    assert "[TOOL]" in tool
    assert "[DONE]" in done
    assert "[ERROR]" in error


def test_json_formatter_output_is_valid_json() -> None:
    formatter = JsonFormatter()
    formatted = formatter.format(
        _make_record(
            "Medical Research Agent completed.",
            "agent_output",
            {"agent": "MedicalResearch", "output": ["Influenza (Flu)"]},
        )
    )
    payload = json.loads(formatted)

    assert payload["level"] == "INFO"
    assert payload["event"] == "agent_output"
    assert payload["meta"]["agent"] == "MedicalResearch"
    assert "timestamp" in payload


def test_timeline_formatter_fallback_for_unknown_event(monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    formatter = TimelineFormatter()
    formatted = formatter.format(_make_record("Custom message", "custom_event", {"agent": "X"}))

    assert "[CUSTOM_EVENT]" in formatted


def test_runtime_timeline_output_and_workflow_schema(monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    logger = logging.getLogger("diagnosmart")
    capture_stream = io.StringIO()
    capture_handler = logging.StreamHandler(capture_stream)
    capture_handler.setFormatter(TimelineFormatter())
    logger.addHandler(capture_handler)

    try:
        run_symptom_analyzer(create_initial_state("I have fever"), llm=None)
    finally:
        logger.removeHandler(capture_handler)

    timeline_output = capture_stream.getvalue()
    assert "[START]" in timeline_output
    assert not timeline_output.strip().startswith("{")

    workflow = build_workflow(llm=None)
    result = workflow.invoke(create_initial_state("I have fever and headache"))
    assert set(["symptoms", "conditions", "advice", "risk_level"]).issubset(result.keys())

