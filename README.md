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

## Models

The default model is `openai/gpt-4o-mini`, but QE Helper uses LiteLLM rather than an OpenAI-specific client. Set a provider-prefixed model in the YAML or pass `--model`; credentials remain in the normal provider environment variables.

```bash
# Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, Ollama, and more
export ANTHROPIC_API_KEY='...'
qe-helper testcases -r '...' --model anthropic/claude-sonnet-4-20250514
qe-helper testplan -r '...' --model gemini/gemini-2.0-flash
qe-helper testcases -r '...' --model ollama/llama3.2
```

## Use a local Claude Code or Cursor CLI

QE Helper can send its generated prompt to a locally installed AI assistant instead of a hosted model API. The assistant's own account/session provides authentication, while QE Helper reads the final response from standard output.

### Claude Code

Install and authenticate Claude Code using Anthropic's normal setup, then confirm it is on your `PATH`:

```bash
claude --version
claude -p "Reply with OK"
```

Use the bundled `claude` profile to generate a QA artifact:

```bash
qe-helper testcases \
  --provider command \
  --command-profile claude \
  --input-file requirements/password-reset.md \
  --output artifacts/password-reset-testcases.md
```

This runs Claude Code in non-interactive print mode (`claude -p --output-format text`).

### Cursor Agent CLI

Install Cursor Agent, log in, and confirm the CLI is available:

```bash
cursor-agent --version
cursor-agent login
cursor-agent status
```

Then select the bundled `cursor` profile:

```bash
qe-helper testplan \
  --provider command \
  --command-profile cursor \
  -r 'Add password reset by email.' \
  --output artifacts/password-reset-test-plan.md
```

The Cursor profile runs `cursor-agent -p --output-format text` and intentionally does **not** pass `--force`, so it does not authorize workspace edits.

### Customize a CLI profile

Create a local config file, then edit its `commands` section to point to another compatible CLI or change the Claude/Cursor flags:

```bash
qe-helper init-config --output qe-prompts.yaml
qe-helper testcases -r '...' --config qe-prompts.yaml --provider command --command-profile claude
```

Every command profile must have a `command` list containing `{prompt}`. QE Helper replaces that item with the complete prompt and executes the argument list directly—not through a shell.

```yaml
commands:
  my-local-assistant:
    command: ["my-assistant", "--print", "{prompt}"]
    timeout_seconds: 180
```

## Build a binary

```bash
pip install -e '.[build]'
pyinstaller --onefile --name qe-helper --collect-data qehelper --collect-all litellm --paths src src/qehelper/__main__.py
```

The resulting executable is in `dist/`. It reads the selected provider's credentials (for example, `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) from the environment; do not embed credentials in the binary.

## Development

```bash
pip install -e '.[dev]'
pytest
```
