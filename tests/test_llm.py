import sys

import pytest

from qehelper.llm import CommandModel, create_model


def test_command_model_requires_prompt_placeholder() -> None:
    with pytest.raises(ValueError, match="prompt"):
        CommandModel(["claude", "-p"])


def test_create_command_model_from_profile() -> None:
    model = create_model(
        {"commands": {"fake": {"command": ["fake-cli", "{prompt}"], "timeout_seconds": 10}}},
        provider_override="command",
        command_profile="fake",
    )
    assert isinstance(model, CommandModel)
    assert model.command == ["fake-cli", "{prompt}"]


def test_command_model_passes_prompt_without_a_shell() -> None:
    model = CommandModel([sys.executable, "-c", "import sys; print(sys.argv[1])", "{prompt}"])
    assert model.invoke("test; $(not-a-command)") == "test; $(not-a-command)"
