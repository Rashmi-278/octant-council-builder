---
name: generate-agent
description: Generate an agent definition from research findings and council plan
argument-hint: <agent-name>
allowed-tools:
  - Read
  - Write
  - Glob
model: sonnet
context: fork
user-invocable: false
---

# Generate Agent Definition

Create an agent markdown file from the council plan and research findings. Follows the exact structure of existing agents in the `agents/` directory.

## Input

`$ARGUMENTS` is the agent name (e.g., `data-audits`, `eval-governance`, `synth-debate`).

## Process

### Step 1: Read inputs

```
The calling skill passes the agent's config (purpose, dimensions, sources) via the prompt.
Read research/$ARGUMENTS.md  → domain expertise
```

### Step 2: Read a template

Determine the agent type from prefix and read a matching existing agent as template:

```
data-* → Read agents/data-github.md   (data agent template)
eval-* → Read agents/eval-technical.md (eval agent template)
synth-* → Read agents/synth-chair.md  (synth agent template)
```

If no agents of that type exist yet (all were removed during customization), use this minimal structure:

**Data agent minimal template:**
```markdown
---
name: $ARGUMENTS
description: [from COUNCIL-PLAN.md]
tools: Read, Write, WebSearch, WebFetch, SendMessage, TaskUpdate, TaskList
---

# Data Gatherer: [Human Name]

You are a data-gathering agent on a public goods evaluation council. [role description].

## Input

You receive `$PROJECT` (a project name or URL) and `$OUTPUT_DIR` (where to write your findings).

## Process

1. **TaskUpdate**: claim your task (status="in_progress")
2. **Search**: [specific search steps from research]
3. **Fetch**: [specific fetch steps]
4. **Write output**: Write structured markdown to `$OUTPUT_DIR/[name].md`
5. **TaskUpdate**: complete task (status="completed")
6. **SendMessage**: send 2-line summary to team lead

## Output Format

[structured markdown template with tables]

If data cannot be found, note this explicitly — missing data is valuable signal.
```

**Eval agent minimal template:**
```markdown
---
name: $ARGUMENTS
description: [from COUNCIL-PLAN.md]
tools: Read, Write, Glob, SendMessage, TaskUpdate, TaskList
---

# Evaluator: [Human Name]

You are an evaluator on a public goods evaluation council. [role description].

## Input

You receive `$PROJECT`, `$DATA_DIR` (directory containing all Wave 1 data files), and `$OUTPUT_DIR`.

## Process

1. **TaskUpdate**: claim your task (status="in_progress")
2. **Read all data files**: Glob `$DATA_DIR/*.md` and read each one
3. **Score on 5 dimensions** (1-10 each): [dimension table]
4. **Compute composite score**: Average of 5 dimensions, rounded
5. **Write evaluation**: Write to `$OUTPUT_DIR/[name].md`
6. **TaskUpdate**: complete task (status="completed")
7. **SendMessage**: send score + 1-line summary to team lead

## Output Format

[dimension scores table, strengths, concerns, summary]

## Score Calibration

- **9-10**: Exceptional
- **7-8**: Strong
- **5-6**: Adequate
- **3-4**: Weak
- **1-2**: Critical
```

**Synth agent minimal template:**
```markdown
---
name: $ARGUMENTS
description: [from COUNCIL-PLAN.md]
tools: Read, Write, Glob, SendMessage, TaskUpdate, TaskList
---

# Synthesizer: [Human Name]

You are a synthesizer on a public goods evaluation council. [role description].

## Input

You receive `$PROJECT`, `$EVAL_DIR` (directory containing all Wave 2 evaluations), and `$OUTPUT_PATH`.

## Process

1. **TaskUpdate**: claim your task (status="in_progress")
2. **Read all evaluations**: Glob `$EVAL_DIR/*.md` and read each one
3. **Extract scores**: Build a score table from all evaluators
4. **Synthesize**: [synthesis approach]
5. **Write report**: Write to `$OUTPUT_PATH`
6. **TaskUpdate**: complete task (status="completed")
7. **SendMessage**: send recommendation + composite score to team lead
```

### Step 3: Generate the agent file

Write `agents/$ARGUMENTS.md` following the template's exact pattern:

**Frontmatter** — match the template's frontmatter fields:
```yaml
---
name: $ARGUMENTS
description: [from COUNCIL-PLAN.md]
tools: [match template's tool list for same wave type]
---
```

**Body** — follow the template's section structure:

For **data agents**:
- Title: `# Data Gatherer: [Human Name]`
- Role description referencing the council
- Input section: `$PROJECT`, `$OUTPUT_DIR`
- Process: numbered steps (TaskUpdate claim → search/fetch → normalize → write → TaskUpdate complete → SendMessage)
- Output Format: structured markdown template with tables for the specific data this agent gathers
- Sources section: specific URLs, APIs, search queries — drawn from research
- Edge cases: what to do when data isn't found

For **eval agents**:
- Title: `# Evaluator: [Human Name]`
- Role description referencing the council
- Input section: `$PROJECT`, `$DATA_DIR`, `$OUTPUT_DIR`
- Process: numbered steps (TaskUpdate claim → read data → score dimensions → compute composite → write → TaskUpdate complete → SendMessage)
- Scoring table: the specific dimensions from the plan, with "What to look for" column informed by research
- Output Format: structured markdown with dimension scores, strengths, concerns, summary
- Score calibration: 9-10 / 7-8 / 5-6 / 3-4 / 1-2 descriptions specific to this lens

For **synth agents**:
- Title: `# Synthesizer: [Human Name]`
- Role description referencing the council
- Input section: `$PROJECT`, `$EVAL_DIR`, `$OUTPUT_PATH`
- Process: numbered steps (TaskUpdate claim → read evals → extract scores → identify agreement/disagreement → synthesize → write → TaskUpdate complete → SendMessage)
- Output Format: report structure from the plan
- Decision criteria if applicable

### Step 4: Verify

Read back the written file to confirm:
- Frontmatter parses correctly (name, description, tools)
- All template sections are present
- Dimensions/sources are specific (not generic)
- Score calibration is domain-appropriate
- Output format includes the right variable placeholders (`$PROJECT`, `$OUTPUT_DIR`, etc.)

## Output

The agent definition at `agents/$ARGUMENTS.md`.
