# Agent instructions (FlowZo)

This file applies to any coding agent (Cursor, Claude Code, Codex, OpenCode, others).

When the user says ponytail, `/ponytail`, "be lazy", YAGNI, or over-engineering: follow [`skills/ponytail/SKILL.md`](skills/ponytail/SKILL.md).

When the user says audit, `/ponytail-audit`, "review the whole repo", or "what can I delete": follow [`skills/ponytail-audit/SKILL.md`](skills/ponytail-audit/SKILL.md). One-shot report, no code changes.

Read those `SKILL.md` files from this repo. Do not require Cursor paths, `.cursor/`, or a host-specific skill installer.

## Regenerating markdown

Do this only when the user asks to regenerate `README.md` and/or the other files in this set. Do not rewrite docs on every code change.

**Template (voice and shape):** the current file on disk. For the root README, that is [`README.md`](README.md) as it exists now — keep its section order, heading text, badge block, emoji, command-block style, and links. Do not invent a new outline.

**Facts:** live sources, not memory.

| Fact | Source |
|------|--------|
| Package name, version, Python, extras, scripts, Hatch `packages` | [`pyproject.toml`](pyproject.toml) |
| Install / test / lint commands | [`pyproject.toml`](pyproject.toml), [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| CLI commands | [`flowzo_cli/main.py`](flowzo_cli/main.py) |
| License | [`LICENSE`](LICENSE), `[project].license` |

**File set** (regenerate together when the user says “README and other markdown”, otherwise only the files they name):

- [`README.md`](README.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/roadmap.md`](docs/roadmap.md)

Leave [`LICENSE`](LICENSE), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), [`docs/legal.md`](docs/legal.md), [`docs/governance.md`](docs/governance.md) unless the user names them.

**Rules**

1. Read the existing markdown first. Rewrite in place. Same sections, updated facts.
2. Drop claims the code and `pyproject.toml` no longer support. Do not add features, stack, or commands that are not in the tree.
3. Keep Hatch note: distribution name is `flowzo`; wheel packages are `flowzo_cli`, `flowzo_ledger`, `flowzo_integrations`.
4. Python version in README/CONTRIBUTING must match `requires-python`.
5. Cross-links stay valid. Do not point at files that do not exist.
6. Do not regenerate [`flowzo_desktop/icons/README.md`](flowzo_desktop/icons/README.md) unless asked.
