# QE Helper

A small command-line assistant for Quality Engineers. It creates test cases and test plans from a short requirement using prompts kept in a YAML file rather than hard-coded in Python.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export OPENAI_API_KEY='...'
qe-helper testcases --requirement 'Users can reset a forgotten password by email.'
qe-helper testplan --requirement 'Add password reset by email.'
qe-helper testcases --input-file requirements/password-reset.md
```

The command writes Markdown to standard output. Save it with `--output` if desired. Requirement input can be supplied inline with `--requirement` or from a UTF-8 `.txt`/`.md` file with `--input-file`; the two options are mutually exclusive.

## Configuration

The default prompts are in `src/qehelper/config/prompts.yaml`. Copy and edit them for project-specific terminology:

```bash
qe-helper init-config --output qe-prompts.yaml
qe-helper testplan -r '...' --config qe-prompts.yaml
```

## Models and IDE CLIs

The default model is `openai/gpt-4o-mini`, but QE Helper uses LiteLLM rather than an OpenAI-specific client. Set a provider-prefixed model in the YAML or pass `--model`; credentials remain in the normal provider environment variables.

```bash
# Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, Ollama, and more
export ANTHROPIC_API_KEY='...'
qe-helper testcases -r '...' --model anthropic/claude-sonnet-4-20250514
qe-helper testplan -r '...' --model gemini/gemini-2.0-flash
qe-helper testcases -r '...' --model ollama/llama3.2
```

For an installed developer-assistant CLI, choose `command` and a configurable profile. The bundled profiles use the official non-interactive print modes for Claude Code (`claude`) and Cursor Agent (`cursor-agent`):

```bash
qe-helper testcases -r '...' --provider command --command-profile claude
qe-helper testplan -r '...' --provider command --command-profile cursor
```

The Cursor profile intentionally does not pass `--force`, so it does not authorize workspace edits. Add other local or IDE CLI tools under `commands` in the copied YAML file. Command arguments are executed directly rather than through a shell.

## Build a binary

```bash
pip install -e '.[build]'
pyinstaller --onefile --name qe-helper --collect-data qehelper --collect-all litellm --paths src src/qehelper/__main__.py
```

The resulting executable is in `dist/`. It reads `OPENAI_API_KEY` from its environment; do not embed keys in the binary.

## Development

```bash
pip install -e '.[dev]'
pytest
```
