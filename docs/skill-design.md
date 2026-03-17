# Skill: design

**Invocable:** Yes
**Args:** `[domain]` (e.g. `"DeFi protocols"`, prompts if omitted)
**Tools:** Read, Write, Glob, Bash, AskUserQuestion, Skill, EnterPlanMode, ExitPlanMode, Agent, WebSearch, WebFetch

## Purpose

Design a custom evaluation council from scratch. Two phases: planning (conversation + structured questions → plan file) then implementation (research + generate + document agents).

## Process

| Step | Action | Phase |
|------|--------|-------|
| 1 | `EnterPlanMode` | Planning |
| 2 | Domain selection. If no `$ARGUMENTS`: ask via `AskUserQuestion`. Invoke `council:design-conversation` with domain. Returns structured summary. | Planning |
| 3 | Roster proposal. Glob existing agents. Present 3 questions: Wave 1 data agents, Wave 2 eval agents, Wave 3 synth approach. Add/remove loop per wave. | Planning |
| 4 | Per-agent config. For each NEW agent: data → ask sources; eval → ask 5 dimensions; synth → ask methodology. Skip existing agents. | Planning |
| 5 | Architecture confirmation. Full preview with approve/revise/cancel. | Planning |
| 5 | Architecture confirmation + `ExitPlanMode` (plan written natively) | Gate |
| 7 | `ExitPlanMode`. Wait for explicit user approval. | Gate |
| 8a | Research wave — spawn background agent per NEW agent. All in single message. Write to `research/{name}.md` | Implementation |
| 8b | Generate wave — spawn background agent per NEW agent. Read plan + research + template. Write to `agents/{name}.md` | Implementation |
| 8c | Doc wave — spawn background agent per NEW agent. Write to `docs/{name}.md` | Implementation |
| 8d | Delete deselected agents from `agents/` and `docs/` | Implementation |
| 8e | Update `README.md` | Implementation |
| 8f | Report created/removed/updated files | Implementation |

## Sub-skills

| Skill | Step | Purpose |
|-------|------|---------|
| `council:design-conversation` | 2 | Conversational domain discovery. Returns: domain, purpose, data priorities, eval priorities, skeptic focus, boundaries, core essence. |

## Template Selection (Step 8b)

| New agent prefix | Template |
|------------------|----------|
| `data-*` | `agents/data-github.md` |
| `eval-*` | `agents/eval-technical.md` |
| `synth-*` | `agents/synth-chair.md` |

Falls back to inline instructions if no template exists.

## Outputs

| File | Description |
|------|-------------|
| native plan file | Structured plan with roster, config, implementation sequence |
| `research/{name}.md` | Domain research per new agent |
| `agents/{name}.md` | Agent definition per new agent |
| `docs/{name}.md` | Documentation per new agent |

## Constraints

- Never skip conversation — structured questions alone miss domain nuance
- Never generate without research — research makes agents domain-specific
- Never spawn agents sequentially — all in single message per wave
- Never modify existing agent definitions — only create new, remove deselected
- Never write plan outside plan mode
- Plan approval is a hard gate — implementation does not auto-start
