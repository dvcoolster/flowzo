# Flowzo Governance & Contribution Guide

This document defines how decisions are made, who owns which areas, and how new contributors can get involved.

---

## 1. Roles & Responsibilities

| Role | Responsibilities | Current Holder |
|------|------------------|----------------|
| **Core Maintainer** | Release cadence, security CVE triage, final merge gate. | @flowzo/maintainers |
| **Bridge Champions** | Own specific adapters (e.g. `mautrix-linkedin`) and publish upgrade guides. | Vacant – apply via Issue comment |
| **Prompt Guild** | Curate AI prompts & evaluation harness. | Vacant |
| **Advisory Board** | Quarterly design review; unblock tie-break decisions. | 3 external maintainers (Matrix, n8n, Chatwoot) – invites pending |
| **Stewards** | Moderate roadmap via Zo World RFC process; can veto breaking changes with rationale. | Core Maintainers + Advisory Board |

---

## 2. Decision-Making Process

* **Minor changes** (< 50 LOC, no public API change) – two-reviewer approval in PR.
* **Substantial changes** – open an **RFC** PR against `docs/rfc/`.  Template lives in `docs/templates/RFC.md`.
* **ADR adoption** – accepted via PR with consensus; tracked in `docs/adr/`.

---

## 3. Contribution Workflow

1. Read `CONTRIBUTING.md` for quick environment setup (< 5 min).
2. Fork & create a feature branch using **Conventional Commits** (`feat:`, `fix:` …).
3. Ensure tests & linter pass (`pnpm test && pnpm lint`).
4. Open PR; auto-labelled with `good-first-issue`, `needs-review`.
5. At least one Champion + one Core Maintainer must approve.

---

## 4. Community Channels

* **Matrix room** – `#zo-inbox-dev:yourserver.com` (primary async chat).
* **GitHub Discussions** – Architecture deep-dives, support Q&A.
* **Monthly Community Call** – 30 min on Jitsi; schedule posted in `docs/meetings/`.

Meeting notes are checked into `docs/meetings/YYYY-MM-DD.md`.

---

## 5. Code of Conduct

Flowzo adheres to the [Contributor Covenant v2.1](https://www.contributor-covenant.org/).  See `CODE_OF_CONDUCT.md`. 