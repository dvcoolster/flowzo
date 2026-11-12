# FlowZo 🎯

> Programmable flow state companion for creators, coders, and teams

[![CI](https://github.com/dvcoolster/flowzo/workflows/CI/badge.svg)](https://github.com/dvcoolster/flowzo/actions)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

FlowZo is a **programmable "flow state" companion** that helps you maintain deep focus and intentional work sessions.

## Features

- 🎯 **Focus Sessions** – Launch timed focus sessions with ambient blockers
- 📋 **Next Step Surfacing** – Pull your next intentional step from GitHub Issues / Linear
- 📊 **Flow Ledger** – Log keystroke/IDE context to build a flow history
- 🔄 **Smooth Re-entry** – Playback last context after interruptions  
- 🔌 **API Integration** – GraphQL & REST APIs for "Is user in flow?" queries

## Quick Start

Requires **Python 3.9+**.

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install FlowZo
pip install -e .

# Start a 25-minute focus session
flowzo start --duration 1500

# Check your next task
flowzo next
```

## Architecture

FlowZo consists of several components:

- **CLI/Daemon** – Core session management and timer
- **Desktop Overlay** – Do-not-disturb UI with progress ring
- **Integrations** – GitHub, Linear, Slack, Notion APIs
- **Flow Ledger** – SQLite/Postgres storage with GraphQL endpoint
- **Web Demo** – Browser-based session starter (WASM timer)

See [docs/architecture.md](docs/architecture.md) for detailed technical design.

## Development

Requires **Python 3.9+**. Hatchling ships `flowzo_cli`, `flowzo_ledger`, and `flowzo_integrations` (the distribution name is `flowzo`).

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
mypy .

# Format code
black .
```

If install fails with `Unable to determine which files to ship inside the wheel`, you need a checkout that includes `[tool.hatch.build.targets.wheel]` in `pyproject.toml`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

AGPL-3.0-only. See [LICENSE](LICENSE) for details.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for the complete development roadmap and execution plan. 