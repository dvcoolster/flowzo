# Flowzo Legal & Compliance

This document tracks licences, third-party ToS caveats, and data-protection commitments so that contributors can make legally-sound decisions without hunting through multiple issues.

---

## 1. Licence

* **AGPL-3.0** for all code under `./` except where explicitly vendored.  
* Dual-licence / commercial offering TBD in governance discussion.
* Every source file MUST include an SPDX header added automatically via CI (see `.github/workflows/addlicense.yml`).

```
// SPDX-Licence-Identifier: AGPL-3.0-only
```

---

## 2. Third-Party ToS & Rate-Limit Risks

| Network | Caveat | Mitigation |
|---------|--------|------------|
| LinkedIn | Unofficial bridge scrapes private APIs → risk of throttling or account ban. | Optional **notifications-only** mode reading email digests; warn users in setup wizard. |
| WhatsApp | `mautrix-whatsapp` puppets a phone client. Meta tolerates, but is unofficial. | Document WhatsApp Business Cloud API migration path for enterprises. |
| Instagram | 2FA and auth flows change frequently; bridging can break silently. | Keep bridge container auto-updated; health-check & alert. |

---

## 3. Data-Processing Agreement (DPA)

For organisations subject to GDPR / CCPA, a template DPA (`docs/legal/dpa-template.md`) is provided.  Self-hosters must update:

1. Data Controller details
2. Data Processing activities
3. Sub-processors list (e.g. Fly.io, OpenAI)
4. International transfer mechanisms (SCCs)

---

## 4. Article 30 Records of Processing

A [data-processing diagram](images/data-processing-overview.drawio) and machine-readable `art30.yaml` enumerate:

* Categories of data subjects & data processed.  
* Purpose & retention periods.  
* Technical & organisational measures.

---

## 5. Regional Deployment Guidance

* **EU-only** – Choose Fly.io `mad` (Madrid) or equivalent; ensure database volumes and object storage remain in-region.  
* WhatsApp puppet phone can connect via WireGuard VPN to EU hosting to avoid cross-border traffic.

---

## 6. Security Policy

* Vulnerability disclosure process in `SECURITY.md` (CVE triage ≤ 72 h).  
* Automatic dependency scanning via GitHub Dependabot.  
* Secret-scan pre-commit hook (`gitleaks`). 