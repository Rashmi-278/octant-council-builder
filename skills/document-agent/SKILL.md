---
name: document-agent
description: Generate a documentation page for a council agent
argument-hint: <agent-name>
allowed-tools:
  - Read
  - Write
  - Glob
model: sonnet
context: fork
user-invocable: false
---

# Generate Agent Documentation

Create a documentation page for a council agent, covering what it does, how it works, and how to customize it.

## Input

`$ARGUMENTS` is the agent name (e.g., `data-audits`, `eval-governance`, `synth-debate`).

## Process

### Step 1: Read inputs

```
Read agents/$ARGUMENTS.md                → agent definition
Read research/$ARGUMENTS.md     → domain context (if exists)
```

Extract from the agent definition:
- Name and description (frontmatter)
- Wave type (from prefix: data/eval/synth)
- Process steps
- Dimensions or sources
- Output format

### Step 2: Write documentation

Write `docs/$ARGUMENTS.md`:

```markdown
# $ARGUMENTS

**Wave:** [1 — Data Gathering | 2 — Evaluation | 3 — Synthesis]
**Role:** [description from frontmatter]

## What This Agent Does

[2-3 sentences explaining the agent's purpose in plain language. What question does it answer? What data does it produce or what judgment does it render?]

## [Data Sources | Scoring Dimensions | Synthesis Method]

[For data agents: table of sources with URLs and what each provides]
[For eval agents: table of dimensions with descriptions and score calibration]
[For synth agents: description of synthesis methodology]

### [Source/Dimension 1]

[1-2 sentences on what this covers and why it matters]

### [Source/Dimension 2]

...

## Output

The agent writes its output to:
- **Data agents:** `council-out/{project}/data/{name}.md`
- **Eval agents:** `council-out/{project}/eval/{name}.md`
- **Synth agents:** `council-out/{project}/REPORT.md`

### Example Output Structure

[Show the key sections of the output format from the agent definition, condensed]

## Customization

### Changing [Sources | Dimensions | Method]

Edit `agents/$ARGUMENTS.md` and modify the [sources table | dimensions table | synthesis section].

### Common Modifications

- [Modification 1: e.g., "Add a new data source by adding a row to the Sources table and a search step in the Process"]
- [Modification 2: e.g., "Change score calibration by editing the calibration table at the bottom"]
- [Modification 3: e.g., "Adjust dimension weights by modifying the composite score calculation"]

## Dependencies

- **Reads from:** [what data this agent needs — e.g., "All Wave 1 data files" or "N/A for data agents"]
- **Consumed by:** [what reads this agent's output — e.g., "All Wave 2 evaluators" or "synth-chair"]
```

### Step 3: Verify

Read back `docs/$ARGUMENTS.md` to confirm:
- All sections are present
- Wave type is correct
- Source/dimension names match the agent definition
- Customization instructions are actionable

## Output

The documentation page at `docs/$ARGUMENTS.md`.
