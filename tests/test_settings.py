from qehelper.settings import load_prompts


def test_default_prompts_have_all_workflows() -> None:
    prompts = load_prompts()
    assert {"testcases", "testplan", "review", "revise"} <= prompts.keys()
    assert "{requirement}" in prompts["testcases"]


def test_cursor_profile_is_noninteractive_for_trusted_workspace() -> None:
    prompts = load_prompts()
    assert "--trust" in prompts["commands"]["cursor"]["command"]
    assert "--force" in prompts["commands"]["cursor"]["command"]
