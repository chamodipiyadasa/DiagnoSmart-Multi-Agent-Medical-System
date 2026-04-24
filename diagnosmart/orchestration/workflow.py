"""LangGraph workflow orchestration for DiagnoSmart."""

from __future__ import annotations

from functools import partial
from typing import Any

from langgraph.graph import END, START, StateGraph

from diagnosmart.agents.diagnosis_generator import run_diagnosis_generator
from diagnosmart.agents.medical_research import run_medical_research
from diagnosmart.agents.risk_validator import run_risk_validator
from diagnosmart.agents.symptom_analyzer import run_symptom_analyzer
from diagnosmart.state.global_state import GlobalState


def build_workflow(llm: Any | None = None):
    """Build and compile the sequential 4-agent LangGraph pipeline.

    Args:
        llm: Optional local LLM instance shared by all agent nodes.

    Returns:
        CompiledStateGraph: Executable LangGraph workflow.
    """
    graph = StateGraph(GlobalState)

    graph.add_node("symptom_analyzer", partial(run_symptom_analyzer, llm=llm))
    graph.add_node("medical_research", partial(run_medical_research, llm=llm))
    graph.add_node("diagnosis_generator", partial(run_diagnosis_generator, llm=llm))
    graph.add_node("risk_validator", partial(run_risk_validator, llm=llm))

    graph.add_edge(START, "symptom_analyzer")
    graph.add_edge("symptom_analyzer", "medical_research")
    graph.add_edge("medical_research", "diagnosis_generator")
    graph.add_edge("diagnosis_generator", "risk_validator")
    graph.add_edge("risk_validator", END)

    return graph.compile()
