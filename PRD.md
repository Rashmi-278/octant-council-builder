# PRD.md – OptInPG Extension for octant-council-builder
**Version:** 1.4 – Production-Ready, Merge-Safe, Railway + Netlify, EAS Attestations  
**Project:** OptInPG (Syntheisi Public Goods Evaluator)  
**Goal:** Turn the existing Claude Council Builder into a real-world-deployable Octant evaluation platform while keeping the original plugin 100% untouched and merge-friendly.  
**Target:** Synthesis.md hackathon + Octant  bounty (all 3 tracks) 
**Base Repo:** https://github.com/golemfoundation/octant-council-builder (we only ADD files/folders)  
**Merge Philosophy:** "Add-only, no overwrites, no deletions, clear comments, optional new feature"

---

## 1. Why This Extension (and Why It's Safe)

The original plugin stays exactly as-is (waves, agent discovery, commands, output format).

We only add new agent `.md` files (auto-discovered), one new command, and one new folder.

Original users can continue using `/council:setup` for any domain without ever seeing our changes.

New `/council:deploy-to-production` is 100% optional — it only runs when explicitly called.

This PR can be merged in <5 minutes by the maintainers with no conflicts.

---

## 2. Design Decisions

**EAS Attestations — not ERC-721.**

We are NOT deploying a new NFT smart contract. Instead, every evaluated project receives an on-chain attestation via the [EAS SDK](https://docs.attest.org/docs/developer-tools/eas-sdk) on Base/Ethereum.

Reasons:
- Simpler to implement — no contract deployment, no gas for contract creation
- Immediately composable with the broader attestation ecosystem
- Attestations are queryable, linkable, and verifiable without a custom indexer
- One shared schema registered once; all project attestations reuse it
- The `eas.attest()` call is a user-triggered action from the dashboard — the pipeline only produces the ready-to-attest JSON, keeping private keys out of the agent system entirely

---

## 3. What We Add (Exact Files — Zero Breaking Changes)

**New folder at repo root:**
```
production/
  backend/
    collector/
    analyst/
    evaluator/
  frontend/
  railway.json
  netlify.toml
  deploy.sh
```

**New files in `agents/` (auto-discovered by existing prefix logic):**
```
data-octant-scraper.md
data-karma.md
data-social-indexer.md
data-global-sources.md
eval-quantitative.md
eval-qualitative.md
eval-ostrom.md
synth-ostrom-report.md
synth-eas-attestation.md
```

**Files we APPEND to only (with clear markers):**
```
SKILL.md    ← append new command section at bottom
CLAUDE.md   ← append reference to new command
```

**New root-level file:**
```
Ostrom-Rules.md   ← exact 8 rules verbatim + source link
```

**New command added cleanly:**
```
/council:deploy-to-production [slug]
```
Exports the current council-out to a live Railway + Netlify app.

**APPEND template for SKILL.md (at the very bottom, after existing content):**
```
=== OPTINPG EXTENSION START ===
/council:deploy-to-production [slug] – Exports the current council to a live
production web app on Railway + Netlify (your existing CLI). Generates 3 modular
FastAPI/LangGraph services + Next.js dashboard with Ostrom radar charts and EAS
attestation records. Safe to ignore for normal users.
=== OPTINPG EXTENSION END ===
```

---

## 4. Core Features (Octant-Native + Ostrom Mechanism)

- Auto-sync real Octant projects (Epoch 11 + historical) from `https://octant.app/projects`
- Global data sources + Karma GAP auto-pull + X/Farcaster/GitHub indexing
- EAS Attestation per project (minted on Base/Ethereum via EAS SDK — no new smart contract)
- Evaluation using exact Elinor Ostrom's 8 Rules (verbatim from earthbound.report article) as the scoring mechanism
- Beautiful production dashboard with interactive Ostrom radar charts, evidence links, and "Attest on Base" button

**This directly wins:**
- Collection track — Karma + Octant scraper
- Analysis track — quant/qual insights
- Mechanism track — Ostrom-Augmented Scoring (Nobel-backed, transparent, on-chain via EAS)

---

## 5. GSTACK Execution Workflow

This PRD is executed using the GSTACK loop. Commands run in sequence. No phase is skipped. **The loop does not stop until 100% of features are built and QA-verified.**

```
/plan-ceo-review → /plan-eng-review → Implement → /review → /ship → /qa
```

---

### Phase 0 — Merge-Safe Setup

1. Create empty folder `production/` at repo root
2. Create `Ostrom-Rules.md` in root (paste exact 8 rules verbatim + source link)
3. Append to `SKILL.md` (at the very bottom, after all existing content) using the template in Section 3
4. Append similar note to `CLAUDE.md`

---

### Phase 1 — Wave 1 Agents (Data Collection)

Create the 4 new `data-*.md` files in `/agents/`.

Each must respect the existing output format (`council-out/{slug}/data/`).

| Agent File | Output | Acceptance Criterion |
|-----------|--------|---------------------|
| `data-octant-scraper.md` | `council-out/{slug}/data/octant.json` | All Epoch 11 projects present; name, address, description, epoch fields; no nulls |
| `data-karma.md` | `council-out/{slug}/data/karma.json` | Karma scores populated; missing projects return `null` with log entry, no crash |
| `data-social-indexer.md` | `council-out/{slug}/data/social.json` | GitHub commits + Farcaster casts + X posts indexed within 7-day window |
| `data-global-sources.md` | `council-out/{slug}/data/global.json` | ≥3 external sources per project (DefiLlama, OSO, L2Beat as applicable) |

---

### Phase 2 — Wave 2 Agents (Analysis + Core Mechanism)

Create the 3 new `eval-*.md` files.

`eval-ostrom.md` must use the exact 8 rules from `Ostrom-Rules.md` and output 0–100 per rule + evidence + confidence.

| Agent File | Output | Acceptance Criterion |
|-----------|--------|---------------------|
| `eval-quantitative.md` | `council-out/{slug}/eval/quant.json` | All numeric scores 0–100; activity, funding efficiency, ecosystem impact fields present |
| `eval-qualitative.md` | `council-out/{slug}/eval/qual.json` | 150–300 word narrative per project citing specific evidence |
| `eval-ostrom.md` | `council-out/{slug}/eval/ostrom-scores.json` | All 8 rules scored; each has: rule_text, score, evidence (non-empty), confidence |

---

### Phase 3 — Wave 3 Agents (Synthesis + Attestation)

Create the 2 new `synth-*.md` files.

`synth-ostrom-report.md` generates a radar chart (SVG/markdown) + final Ostrom score + EAS attestation suggestion block.

`synth-eas-attestation.md` produces EAS SDK-compatible JSON per project. It does NOT call `eas.attest()` — that is a user action from the dashboard.

| Agent File | Output | Acceptance Criterion |
|-----------|--------|---------------------|
| `synth-ostrom-report.md` | `council-out/{slug}/synth/ostrom-report.md` | Valid SVG radar chart embedded; overall Ostrom score 0–100 present; EAS attestation suggestion block included |
| `synth-eas-attestation.md` | `council-out/{slug}/synth/eas-attestations.json` | Valid EAS SDK-compatible JSON per project; schema matches Base attestation format; ready for `eas.attest()` |

**EAS attestation schema:**
```typescript
{
  schemaUID: string,        // registered once on Base; reused for all projects
  recipient: string,        // project wallet address
  data: {
    projectSlug: string,
    ostromScore: uint8,     // 0–100 overall
    rule1Score: uint8,      // through rule8Score: uint8
    evidenceIPFSHash: bytes32,  // IPFS CID of full ostrom-report.md
    epochNumber: uint8,
    evaluatedAt: uint64
  }
}
```

---

### Phase 4 — Production Export

Inside `production/` create:

- `backend/collector/`, `backend/analyst/`, `backend/evaluator/` — LangGraph + FastAPI skeletons that read `council-out/` data
- `frontend/` — Next.js 15 + shadcn dashboard: lists all evaluated Octant projects, clickable Ostrom radar, shareable links, "Attest on Base" button
- `railway.json`
- `netlify.toml`
- `deploy.sh` (uses your existing Railway + Netlify CLI)

The `/council:deploy-to-production` command must:
1. Read the latest `council-out/{slug}/`
2. Generate the above templates populated with real data
3. Output exact commands: `railway up` and `netlify deploy`
4. Print live URLs

---

### Phase 5 — Testing

Add command `/council:test-octant` that runs the full pipeline on:

- Protocol Guild
- L2BEAT
- growthepie
- Revoke.cash
- Tor Project

Output goes to `council-out/test-octant/`

---

### Phase 6 — Final Polish

Update `README.md` by appending a new section at the bottom:

```
### OptInPG Public Goods Extension (optional)
```

With 3-line usage instructions. Ensure original `/council:setup` and all existing commands work unchanged.

---

## 6. QA Acceptance Criteria

QA runs against production only (live Railway + Netlify). Pass/fail is binary. The loop does not end until all tests pass.

### Functional Tests

| Test ID | Feature | Pass Condition |
|---------|---------|---------------|
| QA-F01 | Octant scraper | All Epoch 11 projects in `octant.json`; no nulls |
| QA-F02 | Karma GAP pull | Karma scores populated; missing projects handled gracefully |
| QA-F03 | Social indexer | Activity metrics within 7-day window |
| QA-F04 | Quant evaluator | All numeric fields in range 0–100 |
| QA-F05 | Qual evaluator | 150–300 word narrative per project with cited evidence |
| QA-F06 | Ostrom scorer | All 8 rules scored; evidence strings non-empty |
| QA-F07 | Ostrom report | SVG radar chart embedded; overall score present |
| QA-F08 | EAS attestation records | Valid EAS SDK-compatible JSON; all schema fields typed correctly |
| QA-F09 | Production deploy | Both Railway + Netlify URLs return 200 |
| QA-F10 | Original plugin preserved | `/council:setup` output identical to pre-extension baseline |

### Integration Tests

| Test ID | Scenario | Pass Condition |
|---------|---------|---------------|
| QA-I01–05 | Full pipeline on each of 5 test projects | All 10 functional tests pass end-to-end per project |
| QA-I06 | Concurrent runs (2 slugs) | No data collision in `council-out/` |
| QA-I07 | Upstream API down (Karma) | Fallback triggers; partial data logged; no crash |
| QA-I08 | Empty project data | Graceful error; `errors.json` written |
| QA-I09 | Deploy after full pipeline | Dashboard populated with real data; EAS records visible |
| QA-I10 | Merge to upstream fork | Zero conflicts; maintainer can merge in <5 minutes |

### Performance Tests

| Test ID | Metric | Budget |
|---------|--------|--------|
| QA-P01 | `data-octant-scraper` latency | ≤30s P95 |
| QA-P02 | `eval-ostrom` latency | ≤10s P95 |
| QA-P03 | `synth-ostrom-report` latency | ≤5s P95 |
| QA-P04 | Dashboard load time | ≤3s on 4G / Lighthouse ≥85 |
| QA-P05 | Railway API cold start | ≤8s |

**Loop completion: 25 / 25 tests passing = 100%. Not before.**

---

## 7. Acceptance Criteria (for Merge)

- Original plugin works exactly as before (tested with `/council:setup` on any non-PG domain)
- New agents appear automatically when `/council:setup Public Goods with Ostrom Mechanism` is run
- `/council:deploy-to-production` produces a live dashboard on Netlify + backend on Railway
- No file is overwritten or deleted — only new files + appended sections with clear markers
- All Octant data sources and Ostrom scoring are fully functional on real Epoch 11 projects
- EAS attestation JSON is produced per project and correctly formatted for the EAS SDK

---

## 8. Next Commands to Run (in order)

```
Read this PRD.md
/council:setup Public Goods with Ostrom Mechanism
/council:test-octant
/council:deploy-to-production test-octant
```