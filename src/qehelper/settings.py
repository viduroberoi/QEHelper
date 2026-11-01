from __future__ import annotations

from importlib import resources
from pathlib import Path

import yaml

REQUIRED_PROMPTS = {"testcases", "testplan"}


def load_prompts(config_path: Path | None = None) -> dict[str, str]:
    """Load and validate a user config file or the bundled default."""
    raw = (
        config_path.read_text(encoding="utf-8")
        if config_path
        else resources.files("qehelper.config").joinpath("prompts.yaml").read_text(encoding="utf-8")
    )
    prompts = yaml.safe_load(raw) or {}
    missing = REQUIRED_PROMPTS - prompts.keys()
    if missing:
        raise ValueError(f"Prompt configuration is missing: {', '.join(sorted(missing))}")
    if not all(isinstance(prompts[key], str) for key in REQUIRED_PROMPTS):
        raise ValueError("Each configured prompt must be a string")
    provider = prompts.get("provider", {})
    if provider and not isinstance(provider, dict):
        raise ValueError("'provider' must be a mapping")
    commands = prompts.get("commands", {})
    if commands and not isinstance(commands, dict):
        raise ValueError("'commands' must be a mapping")
    return prompts


def write_default_prompts(destination: Path) -> None:
    destination.write_text(
        resources.files("qehelper.config").joinpath("prompts.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
