from __future__ import annotations

import argparse
from pathlib import Path

from qehelper.llm import create_model
from qehelper.settings import load_prompts, write_default_prompts
from qehelper.workflows import run_workflow

SUPPORTED_INPUT_SUFFIXES = {".txt", ".md"}


def read_requirement_file(path: Path) -> str:
    """Read a plain-text requirement file after validating its type and contents."""
    if path.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_INPUT_SUFFIXES))
        raise argparse.ArgumentTypeError(f"Input file must use one of: {supported}")
    try:
        content = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as error:
        raise argparse.ArgumentTypeError(f"Input file was not found: {path}") from error
    except UnicodeDecodeError as error:
        raise argparse.ArgumentTypeError("Input file must be UTF-8 encoded") from error
    if not content:
        raise argparse.ArgumentTypeError("Input file must not be empty")
    return content


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create QA artifacts from configurable prompts.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    for command in ("testcases", "testplan"):
        subparser = subcommands.add_parser(command, help=f"Generate a {command} Markdown artifact")
        requirement = subparser.add_mutually_exclusive_group(required=True)
        requirement.add_argument("-r", "--requirement", help="Feature or requirement to assess")
        requirement.add_argument(
            "-i", "--input-file", type=Path,
            help="UTF-8 .txt or .md file containing the feature or requirement",
        )
        subparser.add_argument("--config", type=Path, help="Path to a prompts YAML file")
        subparser.add_argument("--provider", choices=("litellm", "command"), help="Override configured provider")
        subparser.add_argument("--model", help="LiteLLM model name, e.g. anthropic/claude-sonnet-4-20250514")
        subparser.add_argument("--command-profile", help="Configured local AI CLI profile, e.g. claude or cursor")
        subparser.add_argument("-o", "--output", type=Path, help="Write Markdown to this file")
    init = subcommands.add_parser("init-config", help="Write the default prompts YAML file")
    init.add_argument("-o", "--output", type=Path, default=Path("qe-prompts.yaml"))
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init-config":
        write_default_prompts(args.output)
        print(f"Created {args.output}")
        return

    prompts = load_prompts(args.config)
    try:
        requirement = args.requirement or read_requirement_file(args.input_file)
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))
    model = create_model(prompts, args.provider, args.model, args.command_profile)
    artifact = run_workflow(model, prompts, args.command, requirement)
    if args.output:
        args.output.write_text(artifact + "\n", encoding="utf-8")
        print(f"Created {args.output}")
    else:
        print(artifact)
