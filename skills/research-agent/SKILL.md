---
name: research-agent
description: Research domain expertise for a council agent before generating its definition
argument-hint: <agent-name>
allowed-tools:
  - Read
  - Write
  - WebSearch
  - WebFetch
  - Glob
model: sonnet
context: fork
user-invocable: false
---

# Research Agent Domain

Research the domain expertise needed to write a high-quality agent definition. Produces a research file that the `generate-agent` skill consumes.

## Input

`$ARGUMENTS` is the agent name (e.g., `data-audits`, `eval-governance`, `synth-debate`).

## Process

### Step 1: Read the plan

```
The calling skill passes the agent's config (purpose, sources/dimensions, research needed) via the prompt. No plan file to read.
```

Find the section for `$ARGUMENTS`. Extract:
- **Purpose** — what this agent does
- **Sources** — specific data sources or APIs (for data agents)
- **Dimensions** — scoring dimensions (for eval agents)
- **Research needed** — what domain knowledge to gather

### Step 2: Research

Based on the agent type (determined by prefix):

**For `data-*` agents:**
- WebSearch for the specific data sources mentioned in the plan
- WebFetch key pages to understand data format and availability
- Look for: API documentation, data schemas, access methods, rate limits
- Look for: alternative sources, cross-referencing approaches

**For `eval-*` agents:**
- WebSearch for evaluation methodologies in this domain
- WebFetch academic or practitioner frameworks for scoring
- Look for: established scoring rubrics, industry benchmarks, common pitfalls
- Look for: what distinguishes excellent from adequate in each dimension

**For `synth-*` agents:**
- WebSearch for synthesis and decision-making frameworks
- Look for: how expert panels aggregate opinions, handling disagreement
- Look for: report formats that decision-makers actually use

### Step 3: Write research file

Write findings to `research/$ARGUMENTS.md`:

```markdown
# Research: $ARGUMENTS

**Researched:** YYYY-MM-DD
**Purpose:** [from plan]

## Domain Context

[2-3 paragraphs of domain background relevant to this agent's role]

## Data Sources Found

[For data agents: specific URLs, APIs, access methods]
[For eval agents: frameworks, rubrics, benchmarks discovered]
[For synth agents: synthesis methodologies, report formats]

### Source 1: [name]
- **URL:** [url]
- **What it provides:** [description]
- **Access method:** [API/scrape/manual]
- **Reliability:** [high/medium/low]

### Source 2: [name]
...

## Methodology Notes

[For eval agents: how to score each dimension based on research]
[For data agents: how to normalize data across sources]
[For synth agents: how to handle disagreement, weighting]

## Key Findings

- [Finding 1 — something that should influence the agent definition]
- [Finding 2]
- [Finding 3]

## Gaps

[What couldn't be found — this is valuable for setting agent expectations]
```

## Output

The research file at `research/$ARGUMENTS.md`, ready for consumption by `generate-agent`.
