# Skill: remove-agent

**Invocable:** Yes
**Args:** `[agent-name]` (e.g. `eval-financial`, optional — prompts if omitted)
**Tools:** Read, Glob, Bash, AskUserQuestion

## Purpose

Remove an agent from the council with impact preview and safety guards.

## Process

| Step | Action |
|------|--------|
| 1 | Glob `agents/{data,eval,synth}-*.md`. Read frontmatter. If arg matches a file, pre-select. Otherwise show roster menu. |
| 2 | **Last-agent guard.** If selected agent is last of its wave type: hard warning for synth (no report without it), soft warning for data/eval. Cancel path available. |
| 3 | Impact preview via `AskUserQuestion`: wave, remaining count, what council loses, downstream impact, files to delete. Confirm or cancel. |
| 4 | Delete files. |
| 5 | Show updated roster with agent counts. |

## Files Deleted

| File | Condition |
|------|-----------|
| `agents/$AGENT.md` | Always |
| `docs/$AGENT.md` | If exists |
| `research/$AGENT.md` | If exists |

## Safety

- No files modified until user confirms in Step 3
- Last-synth-agent gets a hard warning (council produces no report without synth)
- Both guard and confirmation offer cancel paths
