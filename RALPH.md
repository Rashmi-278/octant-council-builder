# RALPH.md — OptInPG GSTACK Execution Document
**Version:** 1.4 — GSTACK-Integrated, EAS Attestations, Merge-Safe  
**Project:** OptInPG (Syntheisi Public Goods Evaluator)  
**Base Repo:** https://github.com/golemfoundation/octant-council-builder  
**Targets:** Synthesis.md hackathon + Octant $5k bounty (all 3 tracks) + public beta

---

> **THE RALPH LOOP DOES NOT STOP UNTIL 100% PROGRESS IS MADE AND ALL FEATURES ARE BUILT.**
> Every phase must pass its exit criteria before the next begins.
> If a phase fails, the loop returns to the top of that phase — not to Phase 01.

---

## GSTACK LOOP

```
/plan-ceo-review → /plan-eng-review → Implement → /review → /ship → /qa
```

Run these commands in sequence. Do not proceed to the next command until the current phase passes all exit criteria.

---

## DESIGN DECISIONS (Read Before Starting)

1. **No ERC-721 smart contracts.** We are NOT deploying a new NFT contract.
2. **EAS attestations instead.** Every evaluated project gets an on-chain attestation via the [EAS SDK](https://docs.attest.org/docs/developer-tools/eas-sdk). This is simpler, cheaper, and immediately composable with the broader attestation ecosystem on Base/Ethereum.
3. **Merge-safe add-only philosophy.** Zero overwrites or deletions to the original Golem Foundation plugin. We only ADD files and APPEND to SKILL.md and CLAUDE.md with clear markers.

---

## PHASE 01 — `/plan-ceo-review`

> **Owner:** CEO / Product Owner  
> **Gate:** Strategic fit, scope freeze, bounty alignment  
> **Ralph does not proceed to Phase 02 until all 6 checks pass.**

### What We Are Building

Turn the existing octant-council-builder Claude plugin into a real-world-deployable Octant evaluation platform. The extension:

- Auto-syncs real Octant projects (Epoch 11 + historical) from `https://octant.app/projects`
- Pulls Karma GAP scores, GitHub activity, and Farcaster/X signals per project
- Evaluates projects using Elinor Ostrom's 8 Rules as the core scoring mechanism (0–100 per rule with evidence)
- Issues EAS attestations on Base for each evaluated project (no new smart contract — pure SDK)
- Deploys a production dashboard (Railway backend + Netlify frontend) with interactive Ostrom radar charts and shareable project links

### Bounty Track Coverage

| Track | How We Win |
|-------|-----------|
| Collection | Karma GAP + Octant scraper + social indexer |
| Analysis | Quant/qual insights with evidence chains |
| Mechanism | Ostrom-Augmented Scoring — Nobel-backed, transparent, on-chain via EAS |

### CEO Review Checklist

- [ ] **Strategic fit** — every feature contributes to at least one of the 3 Octant bounty tracks
- [ ] **Scope is bounded** — implementable without architecture overhaul to the original plugin
- [ ] **Data availability** — Octant API, Karma GAP, GitHub, Farcaster all accessible
- [ ] **EAS design choice confirmed** — using EAS SDK for attestations, no new NFT contract
- [ ] **Merge safety** — zero overwrites to original plugin files confirmed as a hard constraint
- [ ] **Demo-ability** — every feature produces a visible, shareable output (dashboard / score / attestation URL)

### Phase 01 Exit Criteria

All 6 CEO checks pass. Scope is frozen. EAS-over-ERC721 design decision is locked. Engineering may begin.

---

## PHASE 02 — `/plan-eng-review`

> **Owner:** CTO / Lead Engineer  
> **Gate:** Full task breakdown with IDs, owners, inputs, outputs, acceptance tests  
> **Ralph does not proceed to Phase 03 until every task has a complete spec.**

### Files We Will Create (Exact — Zero Breaking Changes)

**New folder at repo root:**
```
production/
  backend/
    collector/      ← FastAPI + LangGraph skeleton (reads council-out/ data)
    analyst/        ← FastAPI + LangGraph skeleton
    evaluator/      ← FastAPI + LangGraph skeleton
  frontend/         ← Next.js 15 + shadcn dashboard
  railway.json
  netlify.toml
  deploy.sh
```

**New agent files in `/agents/` (auto-discovered by existing prefix logic):**
```
agents/
  data-octant-scraper.md
  data-karma.md
  data-social-indexer.md
  data-global-sources.md
  eval-quantitative.md
  eval-qualitative.md
  eval-ostrom.md
  synth-ostrom-report.md
  synth-eas-attestation.md       ← replaces synth-erc721-identity.md
```

**Files we APPEND to only (with clear markers):**
```
SKILL.md      ← append new command section at bottom
CLAUDE.md     ← append reference to new command
```

**New root-level file:**
```
Ostrom-Rules.md   ← exact 8 rules verbatim + source link
```

### New Command

```
/council:deploy-to-production [slug]
```

Reads `council-out/{slug}/` → generates populated Railway + Netlify app → outputs `railway up` and `netlify deploy` commands → prints live URLs.

### APPEND Template for SKILL.md

```
=== OPTINPG EXTENSION START ===
/council:deploy-to-production [slug] – Exports the current council to a live
production web app on Railway (3 FastAPI/LangGraph services) + Netlify (Next.js 15
dashboard). Generates Ostrom radar charts, EAS attestation records, and shareable
project links. Safe to ignore for normal users.
=== OPTINPG EXTENSION END ===
```

### Engineering Task Breakdown

Each task follows this schema: `ID | Agent | Input | Output | Dependencies | Hours | Acceptance Test`

#### Phase 0 — Merge-Safe Setup

| ID | Task | Agent/File | Input | Output | Hours | Acceptance Test |
|----|------|-----------|-------|--------|-------|----------------|
| ENG-001 | Create `production/` folder | — | — | Empty folder at repo root | 0.1h | Folder exists, no other files modified |
| ENG-002 | Create `Ostrom-Rules.md` | — | Earthbound.report article | `Ostrom-Rules.md` at root | 0.5h | All 8 rules present verbatim with source URL |
| ENG-003 | Append to `SKILL.md` | `SKILL.md` | Existing SKILL.md | SKILL.md with extension block | 0.2h | Markers present; original content unchanged |
| ENG-004 | Append to `CLAUDE.md` | `CLAUDE.md` | Existing CLAUDE.md | CLAUDE.md with new command ref | 0.2h | Markers present; original content unchanged |

#### Wave 1 — Data Collection Agents

| ID | Task | Agent | Input | Output | Hours | Acceptance Test |
|----|------|-------|-------|--------|-------|----------------|
| ENG-005 | Octant scraper | `data-octant-scraper.md` | `octant.app/projects` | `council-out/{slug}/data/octant.json` | 3h | All Epoch 11 projects present; no nulls; name, address, description, epoch fields populated |
| ENG-006 | Karma GAP pull | `data-karma.md` | Project slug | `council-out/{slug}/data/karma.json` | 2h | Karma scores populated; missing projects return `null` with log entry, no crash |
| ENG-007 | Social indexer | `data-social-indexer.md` | GitHub org + Farcaster handle | `council-out/{slug}/data/social.json` | 3h | Activity metrics within 7-day window; GitHub commits + Farcaster casts indexed |
| ENG-008 | Global sources | `data-global-sources.md` | Project metadata | `council-out/{slug}/data/global.json` | 2h | At least 3 external sources per project (DefiLlama, OSO, L2Beat as applicable) |

#### Wave 2 — Analysis + Ostrom Mechanism

| ID | Task | Agent | Input | Output | Hours | Acceptance Test |
|----|------|-------|-------|--------|-------|----------------|
| ENG-009 | Quantitative evaluator | `eval-quantitative.md` | `octant.json + karma.json` | `council-out/{slug}/eval/quant.json` | 3h | All numeric scores in range 0–100; activity, funding efficiency, ecosystem impact fields present |
| ENG-010 | Qualitative evaluator | `eval-qualitative.md` | `social.json + global.json` | `council-out/{slug}/eval/qual.json` | 3h | 150–300 word narrative per project citing specific evidence |
| ENG-011 | Ostrom 8-Rule scorer | `eval-ostrom.md` | All eval inputs + `Ostrom-Rules.md` | `council-out/{slug}/eval/ostrom-scores.json` | 4h | All 8 rules scored 0–100; each rule has: rule_text, score, evidence (non-empty string), confidence |

#### Wave 3 — Synthesis + Attestation

| ID | Task | Agent | Input | Output | Hours | Acceptance Test |
|----|------|-------|-------|--------|-------|----------------|
| ENG-012 | Ostrom report + radar | `synth-ostrom-report.md` | `ostrom-scores.json` | `council-out/{slug}/synth/ostrom-report.md` | 3h | Valid SVG radar chart embedded; overall Ostrom score (0–100) present; EAS attestation suggestion block included |
| ENG-013 | EAS attestation records | `synth-eas-attestation.md` | `ostrom-scores.json + quant.json` | `council-out/{slug}/synth/eas-attestations.json` | 3h | Valid EAS schema JSON per project; schema matches Base attestation format; ready for `eas.attest()` call via SDK |

#### Wave 4 — Production Infrastructure

| ID | Task | File | Input | Output | Hours | Acceptance Test |
|----|------|------|-------|--------|-------|----------------|
| ENG-014 | FastAPI collector service | `production/backend/collector/` | `council-out/` data | REST API on `/collect` | 3h | Health endpoint returns 200; `/collect` triggers data-* agents |
| ENG-015 | FastAPI analyst service | `production/backend/analyst/` | Collector output | REST API on `/analyse` | 3h | Health endpoint returns 200; `/analyse` triggers eval-* agents |
| ENG-016 | FastAPI evaluator service | `production/backend/evaluator/` | Analyst output | REST API on `/evaluate` | 3h | Health endpoint returns 200; `/evaluate` triggers synth-* agents |
| ENG-017 | Next.js dashboard | `production/frontend/` | All `council-out/` data | Live Netlify app | 5h | Lists all projects; Ostrom radar is interactive; per-project shareable URLs work; EAS attestation link displayed |
| ENG-018 | `railway.json` + `netlify.toml` | `production/` | — | Config files | 1h | `railway up` and `netlify deploy` succeed |
| ENG-019 | `deploy.sh` | `production/deploy.sh` | Slug | Live URLs printed | 1h | Script exits 0; Railway + Netlify URLs live; runs in <60 seconds |

#### Wave 5 — Commands + Testing

| ID | Task | File | Input | Output | Hours | Acceptance Test |
|----|------|------|-------|--------|-------|----------------|
| ENG-020 | `/council:deploy-to-production` command | `SKILL.md` append | `council-out/{slug}/` | Live URLs + deploy commands | 2h | Reads real data, outputs populated dashboard, prints Railway + Netlify URLs |
| ENG-021 | `/council:test-octant` command | `SKILL.md` append | 5 hardcoded test projects | `council-out/test-octant/` | 1h | Full pipeline on Protocol Guild, L2BEAT, growthepie, Revoke.cash, Tor Project |
| ENG-022 | README append | `README.md` | — | New section at bottom | 0.5h | "### OptInPG Extension (optional)" section with 3-line usage; original README untouched above the marker |

### CTO-Level Technical Standards

- Every new file lives under `agents/`, `production/`, or explicitly approved paths
- All external API calls (Octant, Karma, GitHub, EAS) have typed request/response shapes defined before coding
- Zero new npm/pip packages without explicit CTO approval
- Performance budgets: scraper ≤30s, eval ≤10s, synth ≤5s, dashboard load ≤3s
- Every agent that hits an external API has a timeout, a retry (max 2), and a logged fallback
- Output files are always valid JSON; malformed output fails loudly with a written error file
- EAS SDK calls use env vars for private key and RPC URL — never hardcoded
- All appended sections in SKILL.md and CLAUDE.md wrapped with `=== OPTINPG EXTENSION START/END ===`

### Phase 02 Exit Criteria

All 22 tasks have IDs, owners, inputs, outputs, and acceptance tests. Zero unresolved blockers. EAS attestation schema defined. CTO signs off. Implementation begins.

---

## PHASE 03 — `Implement`

> **Owner:** Engineers  
> **Gate:** Every task from Phase 02 built to spec, unit tests written, self-reviewed  
> **Ralph does not open a PR until all tasks in scope pass their acceptance test locally.**

### Implementation Order (Respect Dependencies)

```
ENG-001 → ENG-002 → ENG-003 → ENG-004   (setup — do first, unblocks everything)
ENG-005 → ENG-006 → ENG-007 → ENG-008   (data agents — can parallelize)
ENG-009 → ENG-010 → ENG-011             (eval agents — need data agents done)
ENG-012 → ENG-013                       (synth agents — need all eval done)
ENG-014 → ENG-015 → ENG-016 → ENG-017  (production services)
ENG-018 → ENG-019                       (deploy config)
ENG-020 → ENG-021 → ENG-022            (commands + README)
```

### Per-Task Checklist (Run for Every ENG-XXX)

- [ ] Pull latest `main`; branch named `feat/ENG-{ID}-{short-desc}`
- [ ] Build to spec — acceptance test from Phase 02 passes locally
- [ ] Write unit test: one test for happy path, one for failure/fallback path
- [ ] Self-review diff — zero files outside approved scope are modified
- [ ] Lint + type check passes with zero errors and zero warnings
- [ ] Task card moved to "In Review"

### Agent File Standard (for all `agents/*.md` files)

Each agent `.md` file must specify:

```markdown
## Agent: [name]
**Prefix:** [data- | eval- | synth-]
**Input:** [exact file path(s)]
**Output:** [exact file path(s)]
**Timeout:** [seconds]
**Fallback:** [what happens when upstream is unavailable]
**Schema:** [JSON shape of output]
```

### EAS Attestation Implementation Notes

Use the `@ethereum-attestation-service/eas-sdk` package.

```typescript
// Schema for OptInPG project attestation
{
  schemaUID: "...",         // register on Base once; reuse for all projects
  recipient: projectAddress,
  data: {
    projectSlug: string,
    ostromScore: uint8,     // 0–100 overall
    rule1Score: uint8,      // ... through rule8Score
    evidenceIPFSHash: bytes32,  // IPFS CID of full ostrom-report.md
    epochNumber: uint8,
    evaluatedAt: uint64
  }
}
```

The `synth-eas-attestation.md` agent outputs the attestation data ready for `eas.attest()`. It does NOT call `eas.attest()` itself in the council pipeline — that is a user action triggered from the dashboard "Attest on Base" button.

### Definition of Done — Implementation

Code compiles. All acceptance tests pass locally. No files outside approved scope are modified. Branch is pushed. PR is open and ready for `/review`.

---

## PHASE 04 — `/review`

> **Owner:** CTO (required) + one peer engineer (required)  
> **Gate:** Two approvals, all checklist items pass, zero open comments  
> **Ralph does not merge or ship until both approvals are recorded.**

### Code Review Checklist

| Category | Check | Pass Condition |
|----------|-------|---------------|
| Spec compliance | Code matches Phase 02 task spec | Zero deviations without written justification in PR |
| Merge safety | No overwrites to original plugin | `git diff main` shows only additions in approved paths |
| Output format | JSON schema matches specified shape | Sample output validated against schema definition |
| EAS schema | Attestation JSON matches Base EAS format | Schema fields match EAS SDK types exactly |
| Error handling | All failure paths covered | No unhandled promise rejections; no bare `except` blocks |
| Tests | Coverage on new code | ≥80% line coverage on new agent files |
| Env vars | No secrets in any tracked file | Grep for private keys, RPC URLs — zero hits |
| Docs | Agent .md files updated | All capabilities reflected in agent spec block |
| Performance | Latency within budget | Benchmark run attached to PR as comment |

### Phase 04 Exit Criteria

Two approvals (CTO + peer). All checklist items pass. No open review comments. PR is ready to merge. `/ship` proceeds.

---

## PHASE 05 — `/ship`

> **Owner:** CTO  
> **Gate:** Both Railway and Netlify live, smoke test passes, original plugin verified  
> **Ralph does not start /qa until both live URLs are confirmed.**

### Ship Checklist

- [ ] Merge PR to `main` — GitHub merge commit SHA logged
- [ ] Run `production/deploy.sh` — script exits 0
- [ ] Railway backend live — `railway up` succeeds; all three health endpoints return 200
- [ ] Netlify frontend live — `netlify deploy` succeeds; dashboard URL accessible
- [ ] Smoke test — `/council:test-octant` runs against live Railway URL
- [ ] Live URLs logged — Railway URL + Netlify URL posted to team channel
- [ ] Original plugin verified — `/council:setup` on a non-PG domain works identically on production

### Rollback Procedure

If any step fails:
1. Immediately revert merge on GitHub
2. Run `railway rollback` and `netlify rollback` to previous deployment
3. Open P0 incident ticket referencing the failed step number
4. Loop returns to **Phase 03 (Implement)** — not Phase 01

### Phase 05 Exit Criteria

Both deployments live. Smoke test passes. Original plugin works. Live URLs documented. `/qa` begins.

---

## PHASE 06 — `/qa`

> **Owner:** QA  
> **Gate:** 100% of all tests pass against production — NOT localhost  
> **The Ralph loop does not terminate until every single test below passes.**

### QA Principles

- All tests run against production (live Railway + live Netlify URL)
- Every acceptance criterion from Phase 02 is tested in the live environment
- Pass/fail is binary — partial pass does not count
- Every failure is logged with: Test ID, actual output, expected output, severity

---

### Functional Test Suite

| Test ID | Feature | Input | Expected Output | Pass Condition |
|---------|---------|-------|----------------|----------------|
| QA-F01 | Octant scraper | Epoch 11 project list URL | `council-out/{slug}/data/octant.json` | All projects present; no nulls; name, address, description, epoch fields populated |
| QA-F02 | Karma GAP pull | Project slug | `council-out/{slug}/data/karma.json` | Karma scores populated; missing projects return `null` with log, no crash |
| QA-F03 | Social indexer | GitHub org + Farcaster handle | `council-out/{slug}/data/social.json` | Activity metrics within 7-day window |
| QA-F04 | Quant evaluator | `octant.json + karma.json` | `council-out/{slug}/eval/quant.json` | All numeric fields in range 0–100 |
| QA-F05 | Qual evaluator | `social.json + global.json` | `council-out/{slug}/eval/qual.json` | 150–300 word narrative per project with cited evidence |
| QA-F06 | Ostrom scorer | All eval inputs | `council-out/{slug}/eval/ostrom-scores.json` | All 8 rules scored; evidence strings non-empty; confidence field present |
| QA-F07 | Ostrom report | `ostrom-scores.json` | `council-out/{slug}/synth/ostrom-report.md` | SVG radar chart embedded; overall score 0–100 present |
| QA-F08 | EAS attestation records | `ostrom-scores.json + quant.json` | `council-out/{slug}/synth/eas-attestations.json` | Valid EAS SDK-compatible JSON per project; all schema fields present and typed correctly |
| QA-F09 | Production deploy | Any valid slug | Live Railway URL + Netlify URL | Both URLs return 200; dashboard shows project data |
| QA-F10 | Original plugin preserved | `/council:setup any-domain` | Unchanged original output | Output identical to pre-extension baseline |

---

### Integration Test Suite

| Test ID | Scenario | Pass Condition |
|---------|---------|----------------|
| QA-I01 | Full pipeline — Protocol Guild | All 10 functional tests pass end-to-end |
| QA-I02 | Full pipeline — L2BEAT | All 10 functional tests pass end-to-end |
| QA-I03 | Full pipeline — growthepie | All 10 functional tests pass end-to-end |
| QA-I04 | Full pipeline — Revoke.cash | All 10 functional tests pass end-to-end |
| QA-I05 | Full pipeline — Tor Project | All 10 functional tests pass end-to-end |
| QA-I06 | Concurrent runs (2 slugs) | Both complete without data collision in `council-out/` |
| QA-I07 | Upstream API down (Karma) | Fallback triggers; partial data logged; no crash; `errors.json` written |
| QA-I08 | Empty project data | Graceful error; `council-out/{slug}/errors.json` written |
| QA-I09 | Deploy after full pipeline | `/council:deploy-to-production` populates dashboard with real data; EAS records visible |
| QA-I10 | Merge PR to upstream fork | Zero conflicts; original plugin maintainer can merge in <5 minutes |

---

### Performance Test Suite

| Test ID | Metric | Budget | Method |
|---------|--------|--------|--------|
| QA-P01 | `data-octant-scraper` latency | ≤30s | P95 over 5 runs on production |
| QA-P02 | `eval-ostrom` latency | ≤10s | P95 over 5 runs on production |
| QA-P03 | `synth-ostrom-report` latency | ≤5s | P95 over 5 runs on production |
| QA-P04 | Dashboard load time (Netlify) | ≤3s on 4G | Lighthouse performance score ≥85 |
| QA-P05 | Railway API cold start | ≤8s | First request after 10-minute idle |

---

### QA Failure Severity

| Severity | Definition | Return To | SLA |
|----------|-----------|-----------|-----|
| P0 — Blocker | Production down or data corruption | Phase 03 Implement | Fix within 2 hours |
| P1 — Critical | Any QA-F or QA-I test fails | Phase 03 Implement | Fix within 4 hours |
| P2 — Major | Performance budget exceeded | Phase 03 Implement | Fix within 8 hours |
| P3 — Minor | Non-blocking cosmetic issue | Logged as tech debt | Next loop iteration |

---

### Loop Completion Criteria

> The Ralph loop is complete when ALL of the following are true:
>
> - ✅ QA-F01 through QA-F10 — all pass
> - ✅ QA-I01 through QA-I10 — all pass  
> - ✅ QA-P01 through QA-P05 — all pass
>
> **Progress = 25 / 25 tests passing = 100%**
>
> Not 90%. Not 99%. **100%.**

---

## LOOP RE-ENTRY RULES

| Failure Detected At | Re-entry Point | Who Resets | What Gets Repeated |
|--------------------|---------------|-----------|-------------------|
| `/plan-ceo-review` | Phase 01 start | CEO | Full CEO review with revised brief |
| `/plan-eng-review` | Phase 02 start | CTO | Full task breakdown revision |
| `Implement` | Phase 03 start | Eng | Only failed tasks, not entire implementation |
| `/review` | Phase 03 start | Eng | Specific failing review items fixed, then re-review |
| `/ship` | Phase 05 start | CTO | Rollback + re-deploy after fix |
| `/qa` | Phase 03 start | Eng | Fix failing features → re-run `/ship` → re-run `/qa` |

---

## ACCEPTANCE CRITERIA MASTER TABLE

Single source of truth. Every row must reach 100% (QA-verified pass) for the loop to complete.

| # | Feature | Role Owner | Acceptance Criterion | QA Test |
|---|---------|-----------|---------------------|---------|
| 1 | Octant Epoch 11 scraper | Eng | Scrapes all projects from `octant.app/projects`; outputs valid `octant.json` with name, address, description, epoch | QA-F01 |
| 2 | Karma GAP integration | Eng | Pulls karma score per project; handles missing projects with `null` + log | QA-F02 |
| 3 | Social indexer | Eng | Indexes GitHub commits + Farcaster casts + X posts within 7-day window | QA-F03 |
| 4 | Global sources agent | Eng | ≥3 external sources per project (DefiLlama, OSO, L2Beat as applicable) | QA-F04, QA-F05 |
| 5 | Quantitative evaluator | Eng | Numeric scores 0–100 for activity, funding efficiency, ecosystem impact | QA-F04 |
| 6 | Qualitative evaluator | Eng | 150–300 word narrative per project with specific cited evidence | QA-F05 |
| 7 | Ostrom 8-Rule scorer | Eng + CTO | All 8 rules scored 0–100 with rule_text, score, evidence, confidence | QA-F06 |
| 8 | Ostrom radar chart | Eng | Valid SVG radar chart embedded in `ostrom-report.md` | QA-F07 |
| 9 | EAS attestation records | Eng | Valid EAS SDK-compatible JSON per project; schema matches Base attestation format; ready for `eas.attest()` | QA-F08 |
| 10 | Railway backend (3 services) | CTO | Collector, analyst, evaluator services deployed; all health endpoints return 200 | QA-P01–03 |
| 11 | Netlify dashboard | Eng | Lists all projects; Ostrom radar interactive; shareable per-project URLs; "Attest on Base" button visible | QA-P04 |
| 12 | `/council:deploy-to-production` | Eng | Reads `council-out/`, populates dashboard, outputs Railway + Netlify URLs in <60s | QA-F09 |
| 13 | `/council:test-octant` | Eng | Full pipeline on 5 test projects; all `council-out/` directories populated correctly | QA-I01–05 |
| 14 | Merge safety | CTO | `git diff main` shows zero modifications to original plugin files; additions only | QA-I10 |
| 15 | Original plugin preservation | CTO | All original commands work identically before and after extension | QA-F10 |

**Progress: 0 / 15 features at 100%**  
*(Update this count after each QA pass)*

---

## EXECUTION COMMANDS

Run in this exact order:

```bash
# 1. Start the loop
/plan-ceo-review

# 2. After CEO approval
/plan-eng-review

# 3. Build
# Implement in order: ENG-001 → ENG-004 → ENG-005–008 → ENG-009–011 → ENG-012–013 → ENG-014–019 → ENG-020–022

# 4. Code review
/review

# 5. Deploy
/ship

# 6. Full QA — loop ends only at 100%
/qa

# Run the test suite manually
/council:setup "Public Goods with Ostrom Mechanism"
/council:test-octant
/council:deploy-to-production test-octant
```

---

## ROLE RESPONSIBILITIES (QUICK REFERENCE)

| Role | Owns | Does NOT own |
|------|------|-------------|
| CEO | Phase 01 — strategic review, scope freeze, design decisions (EAS choice) | Code review, technical architecture |
| CTO | Phase 02 task breakdown, Phase 04 code review, Phase 05 deploy, EAS schema definition | Writing feature code |
| Engineer | Phase 03 implementation, peer review in Phase 04, agent .md files | Scope changes without Phase 02 re-approval |
| QA | Phase 06 — full test suite against production only | Approving partial passes |

---

*RALPH.md v1.4 — OptInPG / Syntheisi Public Goods Evaluator*  
*ERC-721 identity replaced by EAS SDK attestations per design decision locked in Phase 01.*  
*The loop does not stop until progress = 100%.*