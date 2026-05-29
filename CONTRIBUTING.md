# Contributing to AITM

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/aisecuritytools-ai/ai-powered-threat-modeling.git
cd ai-powered-threat-modeling
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Project Structure

- `src/aitm/core/` — Core engine, models, LLM abstraction
- `src/aitm/export/` — Output format generators
- `src/aitm/cli.py` — CLI interface

## Guidelines

- Keep the core engine stateless and provider-agnostic
- All data models go in `core/models.py` (shared contract)
- New export formats go in `export/`
- New AI providers go in `core/llm.py`
- Use Pydantic for all structured data
- Run `ruff check src/` before submitting

## Pull Requests

1. Fork the repo
2. Create a feature branch from `main`
3. Make focused changes
4. Ensure linting passes
5. Submit PR with clear description

## Adding a New Export Format

1. Create `src/aitm/export/your_format.py`
2. Implement a function that takes `ThreatModelResult` and returns string/bytes
3. Add the format option to `cli.py`

## Adding a New AI Provider

1. Add provider to `ModelProvider` enum in `core/config.py`
2. Add `_create_<provider>_llm()` function in `core/llm.py`
3. Update `create_llm()` to route to your function
