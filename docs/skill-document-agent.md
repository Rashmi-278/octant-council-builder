# Skill: document-agent

**Invocable:** No (called by `council:design` and `council:add-agent`)
**Context:** Fork
**Model:** sonnet
**Args:** `<agent-name>` (e.g. `eval-governance`)
**Tools:** Read, Write, Glob

## Purpose

Generate a documentation page for an agent from its definition file.

## Inputs

| File | Required | Purpose |
|------|----------|---------|
| `agents/{name}.md` | Yes | Agent definition — frontmatter, process, dimensions/sources |
| `research/{name}.md` | No | Enriches descriptions if present |

## Output

Writes `docs/{name}.md` with sections:

| Section | Content |
|---------|---------|
| Header | Name, wave, role |
| What This Agent Does | 2-3 sentences |
| Data Sources / Scoring Dimensions / Synthesis Method | Wave-appropriate detail |
| Output | Path + condensed example |
| Customization | Editable fields, 2-3 modification patterns |
| Dependencies | What it reads, what consumes its output |

## Verification

Reads back and confirms:
- All sections present
- Wave type matches prefix
- Source/dimension names match agent definition
- Customization instructions reference specific editable sections
