# Contributing to Flowzo

## Quick start

```bash
pnpm install
docker compose up -d # Postgres, Redis, Synapse, mautrix-whatsapp
pnpm dev:web         # hot-reload PWA
```

## Conventional commits

Use `feat:`, `fix:`, `docs:`, `chore:` prefixes in commit messages.

## Pull-request checklist

- [ ] `pnpm test` & `pnpm lint` pass
- [ ] Docs updated if behaviour/API changed
- [ ] At least one Bridge Champion reviewer requested 