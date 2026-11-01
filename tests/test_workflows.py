from qehelper.workflows import run_workflow


class FakeResponse:
    content = "# Test cases"


class FakeModel:
    def __init__(self) -> None:
        self.prompts: list[str] = []
        self.responses = iter(["# Draft", "Add a negative test", "# Revised artifact"])

    def invoke(self, prompt: str) -> FakeResponse:
        self.prompts.append(prompt)
        response = FakeResponse()
        response.content = next(self.responses)
        return response


def test_workflow_formats_requirement_and_returns_model_content() -> None:
    model = FakeModel()
    prompts = {
        "testcases": "Create: {requirement}",
        "review": "Review {artifact_type}: {requirement}; draft={draft}",
        "revise": "Revise {artifact_type}: {requirement}; draft={draft}; review={review}",
    }
    actual = run_workflow(model, prompts, "testcases", "Password reset")
    assert actual == "# Revised artifact"
    assert model.prompts == [
        "Create: Password reset",
        "Review testcases: Password reset; draft=# Draft",
        "Revise testcases: Password reset; draft=# Draft; review=Add a negative test",
    ]
