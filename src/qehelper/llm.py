from __future__ import annotations

import os
import subprocess
from typing import Protocol



class ChatModel(Protocol):
    def invoke(self, prompt: str) -> object: ...


class LiteLLMModel:
    """Provider-neutral model adapter backed by LiteLLM."""

    def __init__(self, model: str) -> None:
        self.model = model

    def invoke(self, prompt: str) -> str:
        # Keep LiteLLM lazy so command-backed workflows do not initialize cloud
        # provider metadata or require network access.
        from litellm import completion

        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return str(response.choices[0].message.content)


class CommandModel:
    """Adapter for a locally installed, non-interactive AI CLI."""

    def __init__(self, command: list[str], timeout_seconds: int = 180) -> None:
        if "{prompt}" not in command:
            raise ValueError("CLI command must include a '{prompt}' argument")
        self.command = command
        self.timeout_seconds = timeout_seconds

    def invoke(self, prompt: str) -> str:
        args = [part.replace("{prompt}", prompt) for part in self.command]
        try:
            result = subprocess.run(
                args,
                check=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except FileNotFoundError as error:
            raise RuntimeError(f"AI CLI '{args[0]}' is not installed or not on PATH") from error
        except subprocess.CalledProcessError as error:
            detail = error.stderr.strip() or error.stdout.strip() or "no output"
            raise RuntimeError(f"AI CLI failed: {detail}") from error
        return result.stdout.strip()


def create_model(
    settings: dict[str, object], provider_override: str | None = None, model_override: str | None = None,
    command_profile: str | None = None,
) -> ChatModel:
    """Select a cloud provider or locally installed AI CLI from settings and flags."""
    provider_settings = settings.get("provider", {})
    if not isinstance(provider_settings, dict):
        provider_settings = {}
    provider = provider_override or os.getenv("QE_HELPER_PROVIDER") or provider_settings.get("kind", "litellm")
    if provider == "litellm":
        model = model_override or os.getenv("QE_HELPER_MODEL") or provider_settings.get("model")
        if not isinstance(model, str) or not model:
            raise ValueError("A LiteLLM model is required (for example, anthropic/claude-sonnet-4-20250514)")
        return LiteLLMModel(model)
    if provider == "command":
        profiles = settings.get("commands", {})
        profile = command_profile or os.getenv("QE_HELPER_COMMAND_PROFILE") or "claude"
        if not isinstance(profiles, dict) or not isinstance(profiles.get(profile), dict):
            raise ValueError(f"Unknown command profile: {profile}")
        selected = profiles[profile]
        command = selected.get("command")
        if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
            raise ValueError(f"Command profile '{profile}' needs a string command list")
        timeout = selected.get("timeout_seconds", 180)
        return CommandModel(command, timeout if isinstance(timeout, int) else 180)
    raise ValueError("Unknown provider. Use 'litellm' or 'command'.")


def content_from(response: object) -> str:
    content = getattr(response, "content", response)
    return content if isinstance(content, str) else str(content)
