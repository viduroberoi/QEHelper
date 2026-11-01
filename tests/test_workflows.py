from qehelper.workflows import run_workflow


class FakeResponse:
    content = "# Test cases"


class FakeModel:
    def __init__(self) -> None:
        self.prompt = ""

    def invoke(self, prompt: str) -> FakeResponse:
        self.prompt = prompt
        return FakeResponse()


def test_workflow_formats_requirement_and_returns_model_content() -> None:
    model = FakeModel()
    actual = run_workflow(model, "Assess: {requirement}", "Password reset")
    assert actual == "# Test cases"
    assert model.prompt == "Assess: Password reset"
