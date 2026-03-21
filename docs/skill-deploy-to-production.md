# Skill: deploy-to-production

**Invocable:** Yes
**Args:** `<slug>` (lists available slugs if omitted)
**Tools:** Read, Write, Glob, Bash, AskUserQuestion

## Purpose

Exports a completed council evaluation to a live production deployment. Reads `council-out/$SLUG/` and deploys a FastAPI backend to Railway and a Next.js dashboard to Netlify. Supports local preview mode when cloud CLIs aren't available.

## Semantic Tokens

| Token | Source | Value |
|-------|--------|-------|
| `$SLUG` | User input | Slug of the council output to deploy |

## Process

| Step | Action | Tools |
|------|--------|-------|
| 1 | Validate slug — check `council-out/$SLUG/` exists with data/eval/synth subdirs | Bash |
| 2 | Check prerequisites — Railway CLI, Netlify CLI, Python, Node.js | Bash |
| 3 | Stage data — copy council-out into evaluator service directory | Bash |
| 4 | Deploy backend — Railway (3 FastAPI services) or local uvicorn | Bash |
| 5 | Deploy frontend — Netlify (static export) or local Next.js dev server | Bash |
| 6 | Print live URLs — backend, frontend, project page, EAS attestation link | — |

## Deploy Modes

| Mode | Requirements | What happens |
|------|-------------|-------------|
| Full deploy | Railway CLI + Netlify CLI | Backend on Railway, frontend on Netlify |
| Local preview | Python + Node.js | Backend on localhost:8000, frontend on localhost:3000 |
| Artifacts only | None | Files staged, no deployment |

## Production Stack

- **Backend:** 3 FastAPI services (collector, analyst, evaluator) with health endpoints
- **Frontend:** Next.js 15 + Tailwind CSS dashboard with Ostrom radar chart, score breakdowns, governance maturity badges, EAS attestation button
- **Config:** `production/railway.json`, `production/netlify.toml`, `production/deploy.sh`

## Part of OptInPG Extension

This skill is part of the OptInPG extension and does not modify any original plugin files.
