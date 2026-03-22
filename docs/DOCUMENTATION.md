# Octant Council Builder — Complete Documentation

## What Is This?

Council Builder is a **Claude Code plugin** that generates multi-agent evaluation councils. It's not a council itself — it's a factory for building one.

You design a council through conversation. The plugin researches your domain, generates specialized AI agents, and wires them into a three-wave execution pattern. The default agents evaluate Ethereum/Octant public goods projects, but they're scaffolding. Run `/council:setup` and make it yours.

**In plain English:** Imagine you're a grant committee deciding whether to fund a project. Instead of one person reviewing everything, you have 8 independent specialists each looking at a different angle — technical health, community strength, financial sustainability, governance, impact, etc. They never see each other's scores (preventing groupthink). Then a chair reads all the evaluations and writes the final recommendation.

That's what this does, except the specialists are AI agents.

---

## How It Works

### The Three-Wave Pattern

Every evaluation runs in three sequential waves. Within each wave, agents run in parallel.

```
WAVE 1 — DATA GATHERING (8 agents, parallel)
├── Scrape Octant project data
├── Pull Karma accountability scores
├── Index GitHub, Farcaster, X activity
├── Aggregate DefiLlama, OSO, L2Beat data
├── Fetch GitHub repo metrics
├── Assess website and documentation
├── Check on-chain contract activity
└── Compile funding history
         │
         ▼ (gate: wait for ALL data agents to finish)
         │
WAVE 2 — INDEPENDENT EVALUATION (8 agents, parallel)
├── Quantitative scoring (0-100 composite)
├── Qualitative narrative (cited evidence)
├── Ostrom governance scoring (8 principles)
├── Public goods impact assessment
├── Technical health evaluation
├── Community strength assessment
├── Financial sustainability review
└── Skeptic / devil's advocate (red flags)
         │
         ▼ (gate: wait for ALL eval agents to finish)
         │
WAVE 3 — SYNTHESIS (3 agents)
├── Chair → final REPORT.md with recommendation
├── Ostrom Report → radar chart + governance breakdown
└── EAS Attestation → on-chain attestation JSON
```

**Key rule:** Evaluators in Wave 2 never see each other's scores. This independence is enforced architecturally — each agent runs in isolation and writes to its own output file.

### Wave Gates

The orchestrator polls task status after each wave. Wave 2 doesn't start until every Wave 1 agent finishes. Wave 3 doesn't start until every Wave 2 agent finishes. No agent reads partial output.

### Synthesis Can Talk Back

Wave 3 agents can send messages back to Wave 2 evaluators to ask clarifying questions, challenge a score, or request deeper analysis before writing the final report.

---

## Getting Started

### Step 1: Install Settings (one time)

```
/council:settings
```

This enables Claude teams (needed for inter-agent communication) and creates a shell alias.

### Step 2: Run an Evaluation

```
/council:evaluate Protocol Guild
```

This spawns 19 agents across 3 waves and produces a full evaluation report. Takes a few minutes.

### Step 3: Make It Yours

```
/council:setup DeFi lending protocols
/council:setup climate impact DAOs
/council:setup developer tooling grants
```

This runs a conversation to understand your domain, proposes an agent roster, researches each agent's domain, and generates the definitions.

---

## All Commands

| Command | What It Does |
|---------|-------------|
| `/council:settings` | One-time setup — enables Claude teams, creates shell alias, sets permissions |
| `/council:setup [domain]` | Design your council through conversation. Researches domain, proposes agents, generates everything |
| `/council:evaluate <project>` | Run the full 3-wave evaluation. Produces report in `council-out/{slug}/` |
| `/council:add-agent` | Add one new agent via guided conversation + domain research + generation |
| `/council:remove-agent` | Remove an agent with impact preview |
| `/council:deploy-to-production [slug]` | Export to Railway backend + Netlify dashboard (OptInPG extension) |
| `/council:test-octant` | Run evaluation on 5 test Octant projects end-to-end |

---

## All 19 Agents

### Wave 1: Data Agents (8)

These gather raw information from external sources. Each writes to `council-out/{slug}/data/`.

| Agent | Output File | What It Collects |
|-------|------------|-----------------|
| `data-octant-scraper` | `octant.json` | Project data from octant.app — name, address, epoch participation, funding, donors |
| `data-karma` | `karma.json` | Karma GAP scores — accountability rating (0-100), milestones, grants, reputation |
| `data-social-indexer` | `social.json` | 7-day activity from GitHub, Farcaster, X — commits, PRs, casts, posts |
| `data-global-sources` | `global.json` | DefiLlama TVL, Open Source Observer metrics, L2Beat data, Dune, Electric Capital |
| `data-github` | `github.md` | Repo metrics — stars, forks, contributors, issues, PRs, last commit, bus factor |
| `data-web` | `web.md` | Website/docs assessment — mission clarity, team visibility, doc quality, blog cadence |
| `data-onchain` | `onchain.md` | Contract deployments, TVL, usage metrics, developer activity across chains |
| `data-funding` | `funding.md` | Grant history from Gitcoin, RetroPGF, Octant, Giveth, ESP — amounts, diversity, trend |

### Wave 2: Eval Agents (8)

Independent evaluators. Each reads ALL Wave 1 data. Each scores on 5 dimensions (1-10 scale). They never see each other's scores.

| Agent | Output File | What It Evaluates |
|-------|------------|------------------|
| `eval-quantitative` | `quant.json` | 5 weighted dimensions: Activity (25%), Funding Efficiency (20%), Ecosystem Impact (25%), Growth (15%), Transparency (15%). Composite 0-100 |
| `eval-qualitative` | `qual.json` | Narrative assessment (150-300 words), strengths, concerns, context — all with specific citations |
| `eval-ostrom` | `ostrom-scores.json` | Elinor Ostrom's 8 Design Principles scored 0-100 each with evidence and gaps |
| `eval-impact` | `impact.md` | Public goods lens: non-rivalrous, non-excludable, externalities, counterfactual impact, breadth |
| `eval-technical` | `technical.md` | Active development, code quality, contributor health, documentation, technical ambition |
| `eval-community` | `community.md` | User adoption, contributor community, governance, communication, ecosystem integration |
| `eval-financial` | `financial.md` | Funding diversity, sustainability model, efficiency, transparency, runway |
| `eval-skeptic` | `skeptic.md` | Red flags: sybil risk, funding capture, overpromising, conflicts of interest, alternatives, sustainability theater |

### Wave 3: Synth Agents (3)

Read all Wave 2 outputs. Can message evaluators for clarification.

| Agent | Output File | What It Produces |
|-------|------------|-----------------|
| `synth-chair` | `REPORT.md` | Final verdict: FUND / FUND WITH CONDITIONS / DON'T FUND / INSUFFICIENT DATA. Score card, executive summary, agreement/disagreement, key risk |
| `synth-ostrom-report` | `ostrom-report.md` | Embedded SVG radar chart (8 axes), principle-by-principle breakdown, governance recommendations |
| `synth-eas-attestation` | `eas-attestations.json` | EAS SDK-compatible JSON for on-chain attestation on Base. All Ostrom scores + composite |

---

## Expected Output and Artifacts

### Directory Structure

Every evaluation creates this directory structure:

```
council-out/{slug}/
├── data/                          ← Wave 1 output
│   ├── octant.json               — Octant project data
│   ├── karma.json                — Karma GAP accountability scores
│   ├── social.json               — GitHub/Farcaster/X 7-day activity
│   ├── global.json               — DefiLlama, OSO, L2Beat, Dune aggregated data
│   ├── github.md                 — GitHub repo metrics and health
│   ├── web.md                    — Website/docs/team assessment
│   ├── onchain.md                — On-chain contract activity
│   └── funding.md                — Grant funding history
├── eval/                          ← Wave 2 output
│   ├── quant.json                — Quantitative composite score (5 dimensions × 0-100)
│   ├── qual.json                 — Qualitative narrative with citations
│   ├── ostrom-scores.json        — 8 Ostrom principle scores (0-100 each) + evidence
│   ├── impact.md                 — Public goods impact evaluation
│   ├── technical.md              — Technical health evaluation
│   ├── community.md              — Community strength evaluation
│   ├── financial.md              — Financial sustainability evaluation
│   └── skeptic.md                — Red flag / risk assessment
├── synth/                         ← Wave 3 output
│   ├── ostrom-report.md          — Ostrom radar chart + principle breakdown
│   └── eas-attestations.json     — EAS SDK JSON for on-chain attestation
└── REPORT.md                      ← Final council verdict
```

### Artifact Details

#### REPORT.md (Final Verdict)

The main output. Contains:

- **Recommendation**: FUND / FUND WITH CONDITIONS / DON'T FUND / INSUFFICIENT DATA
- **Composite Score**: N/10
- **Score Card**: table of all evaluators with their score and key finding
- **Executive Summary**: 3-4 sentences
- **Areas of Agreement**: where all evaluators converge
- **Areas of Disagreement**: interesting tensions between evaluators
- **Key Risk**: the single most important risk
- **Conditions**: if applicable
- **Methodology**: data sources consulted, evaluator list

**Recommendation criteria:**
| Verdict | Criteria |
|---------|---------|
| FUND | Composite ≥ 7, no critical red flags, clear public good |
| FUND WITH CONDITIONS | Composite 5-7, or addressable red flags |
| DON'T FUND | Composite < 5, critical red flags, not a genuine public good |
| INSUFFICIENT DATA | Not enough information to make a responsible recommendation |

#### ostrom-scores.json (Governance Evaluation)

JSON with 8 Ostrom principle scores (0-100), each containing:
- `score`: numeric score
- `weight`: principle weight (P1, P3, P4 at 1.25x; P5 at 0.75x)
- `evidence`: array of specific findings supporting the score
- `gaps`: array of identified governance gaps
- `sources`: which data files were used

Plus governance maturity assessment: established (60+) / developing (40-59) / nascent (20-39) / absent (<20).

#### ostrom-report.md (Visual Governance Report)

Markdown with:
- Embedded SVG radar chart showing all 8 principle scores
- Principle-by-principle assessment (150-300 words each)
- Combined evaluation (Ostrom + Quant + Qual lenses)
- Strongest and weakest governance areas with recommendations

#### eas-attestations.json (On-Chain Record)

EAS SDK-compatible JSON ready for `eas.attest()` on Base (Chain ID: 8453). Contains:
- Schema definition (Solidity-compatible)
- Attestation object with recipient address, all 8 Ostrom scores, composite score, governance maturity, IPFS hash, epoch, date
- Step-by-step instructions for on-chain submission

**Note:** The agent produces the JSON but does NOT submit on-chain. Private keys are never handled.

#### quant.json (Quantitative Scores)

JSON with 5 scored dimensions:
- Activity (25% weight): GitHub commits, social engagement, recency
- Funding Efficiency (20%): Karma completion, donor diversity, milestone delivery
- Ecosystem Impact (25%): TVL/usage, integrations, dependent projects
- Growth Trajectory (15%): TVL change, contributor growth, funding trend
- Transparency (15%): Open source, public reporting, governance visibility

Calibration: 90-100 exceptional, 70-89 strong, 50-69 moderate, 30-49 below average, 0-29 minimal.

#### qual.json (Qualitative Narrative)

JSON with:
- Summary (150-300 words with specific citations)
- Strengths (2-4 evidence-backed)
- Concerns (1-3 evidence-backed)
- Context (50-100 words on ecosystem fit)
- Signals: public good strength, team signal, community signal, sustainability outlook

---

## Real Example: Protocol Guild Evaluation

Here's what the actual output looks like when you run `/council:evaluate Protocol Guild`:

### Score Card

| Evaluator | Score | Key Finding |
|-----------|-------|-------------|
| Technical | 7/10 | Strong docs, cross-client diversity; frozen contracts by design; low bus factor at coordination layer |
| Community | 9/10 | 187-190 members across 30 teams, 832+ unique donors, unmatched ecosystem integration |
| Financial | 8/10 | $100M+ raised, $57M vesting pipeline, best-in-class transparency; donation-dependent with top-2 donor concentration |
| Impact | 9/10 | Near-ideal public good: non-rival, non-excludable, exceptional externalities, high counterfactual impact |
| Skeptic | 3/10 | Clean — no sybil risk, no sustainability theater, no overpromising |
| Ostrom | 7/10 | Strong boundaries (88) and monitoring (90); weak sanctions (38) and conflict resolution (55) |
| Quantitative | 9/10 | 86/100 composite; ecosystem impact 97/100 is the highest possible |
| Qualitative | 8/10 | Structural trustlessness, proven donor legitimacy; persistent compensation gap |

**Verdict: FUND — 8/10 composite — unconditional funding recommended**

### Ostrom Scores

| Principle | Score | Key Evidence |
|-----------|-------|-------------|
| 1. Clearly Defined Boundaries | 88/100 | On-chain member registry with 187+ named contributors, 6-month minimum threshold |
| 2. Congruence with Local Conditions | 82/100 | 4-year vesting matches L1 development cycle; 1% Pledge model is ecosystem-native |
| 3. Collective-Choice Arrangements | 76/100 | Agora governance, 1-person-1-vote, 33% quorum, working group structure |
| 4. Monitoring | 90/100 | Official Dune dashboards, immutable vesting contract, quarterly updates, public annual report |
| 5. Graduated Sanctions | 38/100 | No documented enforcement ladder; relies on informal social norms |
| 6. Conflict Resolution | 55/100 | Forum + vote exists but no dedicated dispute process, mediator, or appeals |
| 7. Rights to Organize | 78/100 | Legal entity, no external override, immutable contracts; Octant funding dependency |
| 8. Nested Enterprises | 72/100 | Working group + full governance + multisig tiers; embedded in ecosystem funding |

**Overall: 74.5/100 — Established governance maturity**

---

## Ostrom's 8 Design Principles Explained

Elinor Ostrom won the Nobel Prize in Economics (2009) for demonstrating that communities can effectively govern shared resources without privatization or top-down regulation. Her 8 Design Principles (from *Governing the Commons*, 1990) have been translated here from physical commons (fisheries, forests, irrigation systems) to digital public goods (open source code, protocols, data, treasuries).

### Why This Matters for Public Goods

Most grant evaluation asks "Is this a good project?" The Ostrom framework asks "Is this project governed in a way that will sustain itself as a commons?" A project can be technically brilliant but governance-fragile. Ostrom scoring catches that.

### The 8 Principles (Simple Language)

1. **Clearly Defined Boundaries** — Who's in, who's out, and what's the scope? If you can't define who uses and who governs the resource, you can't manage it.

2. **Congruence with Local Conditions** — Are the rules custom-built for this specific context? Copy-pasted DAO templates are a red flag.

3. **Collective-Choice Arrangements** — Can the people affected by the rules actually change them? If stakeholders have no voice, governance is theater.

4. **Monitoring** — Is resource use tracked transparently, and can the community verify it? On-chain dashboards, public financials, open commit history.

5. **Graduated Sanctions** — Do rule violations get proportional responses? First warning, then escalation, not just ban/ignore. This is the hardest for digital projects.

6. **Conflict Resolution** — Can disputes be resolved quickly and cheaply, without lawyers? Governance forums, mediation, appeal mechanisms.

7. **Rights to Organize** — Can the project self-govern without some external entity overriding it? No foundation veto, no hostile regulatory capture.

8. **Nested Enterprises** — Does governance happen at multiple scales? Working groups handle day-to-day, full membership handles structural changes, ecosystem handles cross-project decisions.

### Score Interpretation

| Range | Level | Meaning |
|-------|-------|---------|
| 80-100 | Deeply embedded | This principle is baked into how the project operates |
| 60-79 | Present but incomplete | The governance mechanism exists but has gaps |
| 40-59 | Aspirational | Mentioned or partially attempted, not yet functional |
| 20-39 | Weak | Minimal evidence of this governance practice |
| 0-19 | Absent | No meaningful implementation found |

---

## EAS Attestations Explained

### What Is EAS?

The **Ethereum Attestation Service** is a protocol for making on-chain statements about anything. Think of it as a notarized stamp on the blockchain. When the council evaluates a project, the scores can be permanently recorded on-chain as an attestation.

### What Gets Attested?

| Field | Type | Description |
|-------|------|-------------|
| `projectSlug` | string | URL-safe project identifier |
| `projectWallet` | address | Project's Ethereum address (the attestation recipient) |
| `epochNumber` | uint8 | Octant epoch number |
| `ostromOverallScore` | uint8 | Weighted average of 8 Ostrom principles (0-100) |
| `rule1_boundaries` through `rule8_nestedEnterprises` | uint8 | Individual principle scores (0-100) |
| `quantCompositeScore` | uint8 | Quantitative composite score |
| `governanceMaturity` | string | established / developing / nascent / absent |
| `ipfsReportHash` | string | IPFS hash of the full report |
| `evaluatedAt` | string | Date of evaluation |

### How Does It Work?

1. The `synth-eas-attestation` agent reads all evaluations
2. It produces `eas-attestations.json` with the attestation data
3. A human reviews the JSON and submits it via `eas.attest()` on Base (Chain ID: 8453)
4. The attestation is permanently recorded on-chain

The agent never handles private keys or submits transactions. That's always a human action.

---

## Customization Guide

### Redesign for a New Domain

```
/council:setup DeFi lending protocols
```

This starts a conversation where you:
1. Describe your evaluation domain
2. Review the proposed agent roster
3. Configure each agent's data sources / scoring dimensions
4. The plugin researches each agent's domain
5. Agent markdown files are generated

### Add a Single Agent

```
/council:add-agent
```

Guided flow:
1. Choose wave type (data / eval / synth)
2. Describe the agent's purpose
3. Plugin researches the domain
4. Agent file generated in `agents/`

### Edit Agents Directly

Every agent is a markdown file in `agents/`. Open it, change anything:

- **Data agents**: change which URLs to scrape, what JSON schema to produce
- **Eval agents**: change the 5 scoring dimensions, calibration table, scoring methodology
- **Synth agents**: change the report format, recommendation criteria, output structure

No config file to update. The orchestrator discovers agents by filename prefix.

### Domain Ideas

| Domain | Agents to Add/Swap | Why |
|--------|-------------------|-----|
| DeFi Protocols | `data-audits`, `eval-security` | Security and audit trail matter most |
| L2 Rollups | `data-l2beat`, `eval-decentralization` | L2Beat has detailed data |
| Grant Programs | `data-milestones`, `eval-delivery` | Track record of shipping matters |
| Research Projects | `data-papers`, `eval-novelty` | Academic rigor and novelty |
| Climate DAOs | `data-carbon`, `eval-measurability` | Impact measurement is hard |

### Synthesis Approaches

| Approach | Agents | How |
|----------|--------|-----|
| Single Chair (default) | `synth-chair` | One agent reads all evals, writes unified report |
| Debate | `synth-bull` + `synth-bear` + `synth-chair` | Bull argues FOR, bear AGAINST, chair decides |
| Ranked | `synth-ranker` | Compares project against known alternatives |

---

## Architecture Reference

### Agent Discovery (No Registry)

```
agents/data-*.md  → Wave 1 (data gathering, parallel)
agents/eval-*.md  → Wave 2 (evaluation, parallel, independent)
agents/synth-*.md → Wave 3 (synthesis)
```

Add agent = create a markdown file with the right prefix. Remove agent = delete the file.

### Semantic Tokens

Agent files use `$TOKEN` placeholders that the orchestrator fills in at runtime:

| Token | Meaning |
|-------|---------|
| `$PROJECT` | Project name being evaluated |
| `$SLUG` | URL-safe slug (lowercase, hyphens, max 40 chars) |
| `$DATA_DIR` | Path to Wave 1 data output |
| `$EVAL_DIR` | Path to Wave 2 eval output |
| `$OUTPUT_DIR` | Path to this agent's output directory |
| `$OUTPUT_PATH` | Path to final report |

### Agent Frontmatter

```yaml
---
name: Agent Name
description: One-line description
tools: Read, Write, WebSearch, WebFetch, SendMessage, TaskUpdate
---
```

### Agent Lifecycle

1. `TaskUpdate` — claim the task (status: "in_progress")
2. Do the work (fetch data / score dimensions / synthesize)
3. `Write` — output to `$OUTPUT_DIR/{filename}`
4. `TaskUpdate` — complete the task (status: "completed")
5. `SendMessage` — send summary to team lead

---

## Production Deploy

The OptInPG extension adds deployment capability:

- **Railway Backend**: FastAPI services for data collection, analysis, and evaluation
- **Netlify Frontend**: Next.js 15 dashboard with Ostrom radar charts and shareable links
- **EAS Integration**: On-chain attestation records on Base

```
/council:deploy-to-production protocol-guild
```

Test projects: Protocol Guild, L2BEAT, growthepie, Revoke.cash, Tor Project.

---

## Sharing Your Council

A council is just a repo with markdown files and a plugin manifest. Fork it, redesign the agents, push it, share:

```
fetch https://raw.githubusercontent.com/YOU/YOUR_REPO/main/SKILL.md and follow the instructions
```

No packaging, no publishing, no registry. A council is a repo.
