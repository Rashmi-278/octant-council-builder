# Skill: generate-agent

**Invocable:** No (called by `council:design` and `council:add-agent`)
**Context:** Fork
**Args:** `<agent-name>` (e.g. `eval-governance`)
**Tools:** Read, Write, Glob

## Purpose

Create an agent definition file from plan + research + structural template.

## Inputs

| File | Purpose |
|------|---------|
| the calling skill's prompt | Agent config: description, dimensions, sources |
| `research/{name}.md` | Domain expertise from research step |
| Template agent (see below) | Structural pattern to follow |

## Template Selection

| Prefix | Template |
|--------|----------|
| `data-*` | `agents/data-github.md` |
| `eval-*` | `agents/eval-technical.md` |
| `synth-*` | `agents/synth-chair.md` |

Falls back to inline instructions if no template of that type exists.

## Output Structure by Wave

| Wave | Title | Input tokens | Process | Key sections |
|------|-------|-------------|---------|-------------|
| `data-*` | `# Data Gatherer: [Name]` | `$PROJECT`, `$OUTPUT_DIR` | TaskUpdate → search/fetch → normalize → write → TaskUpdate → SendMessage | Sources, Output Format, Edge Cases |
| `eval-*` | `# Evaluator: [Name]` | `$PROJECT`, `$DATA_DIR`, `$OUTPUT_DIR` | TaskUpdate → read data → score 5 dimensions → composite → write → TaskUpdate → SendMessage | Scoring Table, Calibration (9-10/7-8/5-6/3-4/1-2) |
| `synth-*` | `# Synthesizer: [Name]` | `$PROJECT`, `$EVAL_DIR`, `$OUTPUT_PATH` | TaskUpdate → read evals → extract scores → agreement/disagreement → synthesize → write → TaskUpdate → SendMessage | Decision Criteria, Output Format |

## Verification

After writing, reads back and checks:
1. Frontmatter has `name`, `description`, `tools`
2. All template sections present
3. Dimensions/sources are domain-specific (not placeholders)
4. Correct `$TOKEN` placeholders for wave type
