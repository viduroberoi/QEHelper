from qehelper.settings import load_prompts


def test_default_prompts_have_all_workflows() -> None:
    prompts = load_prompts()
    assert {"testcases", "testplan", "review", "revise"} <= prompts.keys()
    assert "{requirement}" in prompts["testcases"]
