# Contributing to FlowZo

## Quick start

Requires **Python 3.9+**.

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

```bash
pytest
ruff check .
mypy .
```

Desktop overlay: see `flowzo_desktop/` (Node + Rust/Tauri). That is optional for Python CLI work.

## Conventional commits

Use `feat:`, `fix:`, `docs:`, `chore:` prefixes in commit messages.

## Pull-request checklist

- [ ] `pytest`, `ruff check .`, and `mypy .` pass
- [ ] Docs updated if behaviour/API changed
