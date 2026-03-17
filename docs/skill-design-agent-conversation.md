# Skill: design-agent-conversation

**Invocable:** No (called by `council:add-agent`)
**Args:** `<wave-type> [name-hint]` (e.g. `"eval governance"`)
**Tools:** Read, Write

## Purpose

Focused dialogue to design a single agent. Scoped to one agent within an already-decided council — never revisits council-level questions.

## Args

| Arg | Required | Values |
|-----|----------|--------|
| `wave-type` | Yes | `data`, `eval`, `synth` |
| `name-hint` | No | Starting name context (e.g. `governance`, `audits`) |

## Wave-Specific Probes

| Wave | Probes for |
|------|-----------|
| `data` | Specific APIs/URLs, data format, key metrics, missing-data fallback |
| `eval` | 5 scoring dimensions, what distinguishes 6 vs 8, priority when dimensions conflict, supporting evidence in data files |
| `synth` | Audience, output structure, handling evaluator disagreement |

## Stop Conditions

| Field | Required |
|-------|----------|
| Agent name (`wave-name`) | Yes |
| One-line description | Yes |
| Detailed purpose (2-3 sentences) | Yes |
| Sources (data) / 5 dimensions (eval) / output structure (synth) | Yes |
| Research brief (what domain knowledge to gather) | Yes |

## Exit Summary

```
**Name:** [wave]-[name]
**Description:** ...
**Purpose:** ...
**[Sources / Dimensions / Method]:** ...
**Research needed:** ...
```

## Difference from design-conversation

`design-conversation` = council-level (domain, purpose, scope, roster).
`design-agent-conversation` = single agent within an established council.
