# Flowzo Roadmap

> **TL;DR (10-line executive summary)**  
> **Problem** – Modern professionals juggle LinkedIn, Slack, WhatsApp, e-mail, Instagram DMs and X DMs, losing flow and context.  
> **End-state** – One keyboard-first inbox that ingests every channel, suggests AI drafts in < 2 s and can be self-hosted or one-click-deployed.  
> **Risks** – (1) WhatsApp Web protocol breakage; (2) LLM vendor price spikes; (3) PII leakage via mis-configured logging.  
> **Mitigations** – Bridge bake-off & alerting, cost-cap thresholds + model fall-backs, structured redaction & DLP CI checks.  
> **Next 90 days** – Docker dev-stack, first React PWA, AI draft micro-service.  
> **Success KPI v0** – Median time-to-zero-inbox under 4 min, 70 % AI draft acceptance rate.  
> **Team** – 4 FTE engineers + product lead + designer.  
> **Licence** – AGPL-3.0 open-core; dual-licence possible for enterprise.  
> **Community** – Matrix room `#zo-inbox-dev` + GitHub Discussions.

---

## 1. Problem Statement & Success Criteria

See the [Personas & KPIs](#personas--primary-use-cases) and [Key Metrics](#key-metrics--kpis) sections for detailed framing.

|   |   |
|---|---|
| **Mission** | Reduce cognitive load by funnelling every message into one blazing-fast, keyboard-centric interface. |
| **Definition of Done (MVP)** | 1️⃣ Unified stream for Gmail/IMAP, one Slack workspace, one WhatsApp account and one LinkedIn account.<br/>2️⃣ "Draft-reply" button suggests response within **< 2 s**.<br/>3️⃣ Distributed as **AGPL-3.0** with one-click deploy to Fly.io. |


## 2. High-Level Architecture

The architecture diagram and deep-dive live in [architecture.md](architecture.md).  This keeps the roadmap skimmable and lets the diagram render faster in GitHub.


## 3. Execution Roadmap

Navigate directly to a phase:
[Phase 0](#phase-0--foundry) · [Phase 1](#phase-1--first-inbox) · [Phase 2](#phase-2--ai-drafts) · [Phase 3](#phase-3--linkedin--slack-bridges) · [Phase 4](#phase-4--search--priority) · [Phase 5](#phase-5--privacy--compliance) · [Phase 6](#phase-6--v1-oss-launch)

### Phase 0 — Foundry

| Task | Owner | Effort (SP) | Dependencies |
|------|-------|-------------|--------------|
| Initialise mono-repo skeleton | Eng Lead | 3 | — |
| CI (lint, test, build) & DCO check | Eng Lead | 2 | — |
| Docker-compose dev-stack (Postgres, Redis, Synapse, `mautrix-whatsapp`) | Backend | 8 | Skeleton repo |
| Gmail IMAP importer → Event Bus | Backend | 5 | Dev-stack |
| Smoke test: WhatsApp & email events visible | QA | 3 | Above |

### Phase 1 — First Inbox

| Task | Owner | Effort (SP) | Dependencies |
|------|-------|-------------|--------------|
| Scaffold React PWA (Vite, TS, Tailwind) | Frontend | 5 | Repo skeleton |
| Integrate keyboard layer (Superhuman clone) | Frontend | 3 | PWA |
| WebSocket client (NATS JS) | Frontend | 5 | Dev-stack |
| List/Detail view & hotkeys (`j/k`, `r`) | Frontend | 8 | Above |
| E2E: read & reply email + WhatsApp | QA | 5 | All tasks |

### Phase 2 — AI Drafts

| Task | Owner | Effort | Dependencies |
|------|-------|--------|--------------|
| `draft` tRPC service wrapping LLM | AI Eng | 8 | Dev-stack |
| Diff UI & accept shortcut (`⌘+↵`) | Frontend | 3 | PWA |
| Benchmark < 2 s latency | AI Eng | 3 | Service |

### Phase 3 — LinkedIn & Slack Bridges

| Task | Owner | Effort | Dependencies |
|------|-------|--------|--------------|
| Deploy `mautrix-linkedin` | Bridge Champ | 5 | Dev-stack |
| Deploy `matterbridge` Slack gateway | Bridge Champ | 3 | Dev-stack |
| Map IDs → `channel_id` table | Backend | 5 | Bridges |
| Round-trip messaging all 4 networks | QA | 5 | Above |

### Phase 4 — Search & Priority

*(Details trimmed for brevity; full spec in Phase 4 ADR.)*

### Phase 5 — Privacy & Compliance

*(See [legal.md](legal.md).)*

### Phase 6 — v1 OSS Launch

*(See [governance.md](governance.md) for community plan.)*


## 4. Personas & Primary Use-Cases

| Persona | Top Jobs-To-Be-Done |
|---------|--------------------|
| **Founder** | Triage 100+ investor & customer pings per day without context-switching. |
| **Team Lead** | Follow threads across Slack channels & email while staying in flow during stand-up. |
| **Solopreneur** | Respond to DMs across platforms within < 1 h to maintain brand presence. |
| **Executive Assistant** | Schedule replies for busy execs and draft templated responses. |


## 5. Key Metrics / KPIs

| Metric | Target | Notes |
|--------|--------|-------|
| Median time-to-zero-inbox | < 4 min | From opening UI to clear state. |
| Draft accuracy | ≥ 70 % edits unchanged | Measures LLM reply usefulness. |
| Bridge MTTR | < 48 h | After upstream API change. |


## 6. References & Next Steps

* Architecture deep-dive → [architecture.md](architecture.md)  
* Legal & compliance → [legal.md](legal.md)  
* Community & governance → [governance.md](governance.md)

Open **Issue #4** — "Define KPIs & Personas" and assign to Product Lead. 