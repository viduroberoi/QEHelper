from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from qehelper.llm import ChatModel, content_from


class WorkflowState(TypedDict):
    requirement: str
    prompt_template: str
    result: str


def build_workflow(model: ChatModel):
    """Build a single-node graph, leaving room for review nodes later."""
    def generate(state: WorkflowState) -> dict[str, str]:
        prompt = state["prompt_template"].format(requirement=state["requirement"])
        return {"result": content_from(model.invoke(prompt))}

    graph = StateGraph(WorkflowState)
    graph.add_node("generate", generate)
    graph.add_edge(START, "generate")
    graph.add_edge("generate", END)
    return graph.compile()


def run_workflow(model: ChatModel, prompt_template: str, requirement: str) -> str:
    result = build_workflow(model).invoke(
        {"requirement": requirement, "prompt_template": prompt_template, "result": ""}
    )
    return result["result"]
