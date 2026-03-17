# Skill: research-agent

**Invocable:** No (called by `council:design` and `council:add-agent`)
**Context:** Fork
**Args:** `<agent-name>` (e.g. `data-audits`, `eval-governance`)
**Tools:** Read, Write, Glob, WebSearch, WebFetch

## Purpose

Gather domain expertise for a single agent before its definition is generated. Reads the plan, performs web research, writes structured findings.

## Process

1. Read the calling skill's prompt → find agent's section (purpose, sources/dimensions, research needed)
2. Research strategy by prefix:

| Prefix | Searches for |
|--------|-------------|
| `data-*` | API docs, data schemas, access methods, rate limits, alternatives |
| `eval-*` | Evaluation methodologies, scoring rubrics, benchmarks, what distinguishes excellent from adequate |
| `synth-*` | Synthesis frameworks, panel aggregation, handling disagreement, report formats |

3. Write to `research/{name}.md`

## Output Format

```
# Research: {name}
Researched: YYYY-MM-DD
Purpose: [from plan]

## Domain Context
## Data Sources Found
## Methodology Notes
## Key Findings
## Gaps
```
