from __future__ import annotations

from typing import Mapping, TypedDict

from langgraph.graph import END, START, StateGraph

from qehelper.llm import ChatModel, content_from


class WorkflowState(TypedDict):
    artifact_type: str
    requirement: str
    artifact_template: str
    review_template: str
    revise_template: str
    draft: str
    review: str
    result: str


def build_workflow(model: ChatModel):
    """Build a generate, review, and revision workflow for QA artifacts."""
    def generate(state: WorkflowState) -> dict[str, str]:
        prompt = state["artifact_template"].format(requirement=state["requirement"])
        return {"draft": content_from(model.invoke(prompt))}

    def review(state: WorkflowState) -> dict[str, str]:
        prompt = state["review_template"].format(
            artifact_type=state["artifact_type"],
            requirement=state["requirement"],
            draft=state["draft"],
        )
        return {"review": content_from(model.invoke(prompt))}

    def revise(state: WorkflowState) -> dict[str, str]:
        prompt = state["revise_template"].format(
            artifact_type=state["artifact_type"],
            requirement=state["requirement"],
            draft=state["draft"],
            review=state["review"],
        )
        return {"result": content_from(model.invoke(prompt))}

    graph = StateGraph(WorkflowState)
    graph.add_node("generate", generate)
    graph.add_node("review", review)
    graph.add_node("revise", revise)
    graph.add_edge(START, "generate")
    graph.add_edge("generate", "review")
    graph.add_edge("review", "revise")
    graph.add_edge("revise", END)
    return graph.compile()


def run_workflow(
    model: ChatModel, prompts: Mapping[str, str], artifact_type: str, requirement: str
) -> str:
    """Generate an artifact, review it against the requirement, then apply the fixes."""
    result = build_workflow(model).invoke(
        {
            "artifact_type": artifact_type,
            "requirement": requirement,
            "artifact_template": prompts[artifact_type],
            "review_template": prompts["review"],
            "revise_template": prompts["revise"],
            "draft": "",
            "review": "",
            "result": "",
        }
    )
    return result["result"]
