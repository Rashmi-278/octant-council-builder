# Skill: evaluate

**Invocable:** Yes
**Args:** `<project-name-or-url>` (prompts if omitted)
**Tools:** Read, Write, Glob, Bash, AskUserQuestion, Agent, SendMessage, TaskCreate, TaskUpdate, TaskList, TeamCreate, TeamDelete

## Purpose

Orchestrates the full council evaluation: discovers agents, creates a team, spawns three waves sequentially, gates between waves, and presents the final report.

## Semantic Tokens

| Token | Source | Value |
|-------|--------|-------|
| `$PROJECT` | User input | Project name or URL |
| `$SLUG` | Derived | URL-safe slug (lowercase, hyphens, max 40 chars) |
| `$DATA_DIR` | Constructed | `council-out/$SLUG/data` |
| `$EVAL_DIR` | Constructed | `council-out/$SLUG/eval` |
| `$OUTPUT_DIR` | Per-agent | Agent's wave output directory |
| `$OUTPUT_PATH` | Constructed | `council-out/$SLUG/REPORT.md` |

## Process

| Step | Action | Tools |
|------|--------|-------|
| 1 | Parse input → `$PROJECT` + `$SLUG`. Glob `agents/{data,eval,synth}-*.md`. Read frontmatter. Create `council-out/$SLUG/{data,eval}`. Show roster, confirm. | Glob, Read, Bash, AskUserQuestion |
| 2 | Create team `council-$SLUG`. Pre-create tasks for all agents across all waves. | TeamCreate, TaskCreate |
| 3 | **Wave 1** — Spawn ALL `data-*` agents in single message (`run_in_background=true`). Poll `TaskList` until all Wave 1 tasks complete. | Agent, TaskList |
| 4 | **Wave 2** — Spawn ALL `eval-*` agents in single message. Poll until complete. | Agent, TaskList |
| 5 | **Wave 3** — Spawn ALL `synth-*` agents. Poll until complete. | Agent, TaskList |
| 6 | Present `REPORT.md` to user. Offer: done / evaluate another / dig deeper. | AskUserQuestion |
| 7 | Broadcast shutdown. Delete team. | SendMessage, TeamDelete |

## Wave Gates

Each wave spawns all agents in a **single message** for parallelism. Orchestrator polls `TaskList` until every task in that wave shows `status="completed"`. Only then proceeds to next wave.

## Agent Discovery

```
Glob agents/data-*.md  →  Wave 1 agents
Glob agents/eval-*.md  →  Wave 2 agents
Glob agents/synth-*.md →  Wave 3 agents
```

No hardcoded roster. Add/remove files to change the council.

## Output

```
council-out/$SLUG/
├── data/        ← one .md per data agent
├── eval/        ← one .md per eval agent
└── REPORT.md    ← synth output
```

## Constraints

1. Never skip wave gate — all agents in wave must complete before next wave starts
2. Evaluators read `data/` only, never `eval/` — independence is enforced
3. Never fabricate data — agents report absence, not invention
4. Never spawn agents one at a time — all in single message per wave
5. Never synthesize in orchestrator — that's the synth agent's job
