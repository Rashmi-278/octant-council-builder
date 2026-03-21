---
description: Run the full evaluation pipeline on 5 test Octant projects to verify all agents work end-to-end
argument-hint:
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - Agent
  - Task
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TeamCreate
  - TeamDelete
  - SendMessage
  - WebFetch
  - WebSearch
  - AskUserQuestion
model: opus
context: inherit
user-invocable: true
---

# Test Octant Pipeline

Run the full council evaluation pipeline on 5 hardcoded Octant projects to verify all agents work end-to-end. Output goes to `council-out/test-octant/`.

This is a validation command — it exercises every agent (data, eval, synth) on real projects to confirm the OptInPG extension works correctly.

<progress>
- [ ] Step 1: Confirm test run
- [ ] Step 2: Run evaluations on all 5 projects
- [ ] Step 3: Validate outputs
- [ ] Step 4: Report results
</progress>

## Test Projects

These 5 projects are hardcoded for testing:

1. **Protocol Guild** — Ethereum core contributor funding
2. **L2BEAT** — L2 analytics and risk assessment
3. **growthepie** — L2 ecosystem analytics
4. **Revoke.cash** — Token approval management
5. **Tor Project** — Privacy infrastructure

## Step 1: Confirm Test Run

```
AskUserQuestion:
  question: "Run full pipeline test on 5 Octant projects?"
  header: "Test Octant"
  options:
    - label: "Run all 5"
      description: "Full pipeline: data → eval → synth for each project"
      preview: |
        Projects: Protocol Guild, L2BEAT, growthepie, Revoke.cash, Tor Project
        Output: council-out/test-octant/

        This will run ALL agents (data-*, eval-*, synth-*) on each project.
        Estimated time: depends on agent count and API response times.
    - label: "Run 1 project only"
      description: "Quick test with Protocol Guild only"
    - label: "Cancel"
      description: "Don't run tests"
```

If "Cancel" → stop.
If "Run 1 project only" → only run Protocol Guild, skip to Step 2 with projects = ["Protocol Guild"].

## Step 2: Run Evaluations

For each test project, invoke the `evaluate` skill:

```
projects = ["Protocol Guild", "L2BEAT", "growthepie", "Revoke.cash", "Tor Project"]
```

Run them sequentially (to avoid overwhelming external APIs):

For each project:
1. Use the Skill tool to invoke `council:evaluate` with the project name
2. Wait for completion
3. Log result (success/failure)

All output goes under `council-out/` with each project's slug:
- `council-out/protocol-guild/`
- `council-out/l2beat/`
- `council-out/growthepie/`
- `council-out/revoke-cash/`
- `council-out/tor-project/`

## Step 3: Validate Outputs

After all evaluations complete, verify each project's output:

```bash
# For each project slug, check:
# 1. Data files exist
ls council-out/$SLUG/data/

# 2. Eval files exist
ls council-out/$SLUG/eval/

# 3. Synth files exist (if synth agents ran)
ls council-out/$SLUG/synth/ 2>/dev/null || echo "No synth output"

# 4. Report exists
test -f council-out/$SLUG/REPORT.md && echo "REPORT.md: OK" || echo "REPORT.md: MISSING"
```

Check specific acceptance criteria:
- **QA-F01**: `octant.json` exists and has data
- **QA-F02**: `karma.json` exists, missing projects handled gracefully
- **QA-F03**: `social.json` exists with activity metrics
- **QA-F04**: `quant.json` has all numeric fields 0-100
- **QA-F05**: `qual.json` has 150-300 word narrative
- **QA-F06**: `ostrom-scores.json` has all 8 rules scored with non-empty evidence
- **QA-F07**: `ostrom-report.md` has SVG radar chart and overall score
- **QA-F08**: `eas-attestations.json` has valid EAS SDK-compatible JSON

## Step 4: Report Results

Present a summary table:

```
=== Test Octant Results ===

| Project | Data | Eval | Synth | Report | Status |
|---------|------|------|-------|--------|--------|
| Protocol Guild | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | PASS/FAIL |
| L2BEAT | ... | ... | ... | ... | ... |
| growthepie | ... | ... | ... | ... | ... |
| Revoke.cash | ... | ... | ... | ... | ... |
| Tor Project | ... | ... | ... | ... | ... |

Passed: X/5
Failed: X/5

Output directory: council-out/
```

If any project failed, show which specific files are missing or malformed.
