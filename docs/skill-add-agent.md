# Skill: add-agent

**Invocable:** Yes
**Args:** `[wave] [name]` (e.g. `eval governance`, both optional)
**Tools:** Read, Write, Glob, Bash, AskUserQuestion, Skill, Agent, WebSearch, WebFetch

## Purpose

Add a new agent to the council: conversation → research → generate → document → update roster.

## Process

| Step | Action |
|------|--------|
| 1 | Glob `agents/{data,eval,synth}-*.md`. Display roster by wave. If `$ARGUMENTS` has wave, store as `$WAVE` and skip selection. Otherwise ask. |
| 2 | Invoke `council:design-agent-conversation` with `$WAVE` and `$NAME`. Extracts: name, description, purpose, sources/dimensions, research brief. |
| 3 | Append plan entry to plan context. Spawn research sub-agent → writes `research/$WAVE-$NAME.md` |
| 4 | Resolve template (`data-github.md` / `eval-technical.md` / `synth-chair.md`). Spawn generate sub-agent → writes `agents/$WAVE-$NAME.md` |
| 5 | Spawn doc sub-agent → writes `docs/$WAVE-$NAME.md` |
| 6 | Update `README.md` flow diagram. Report created files. |

## Sub-skills

| Skill | Step |
|-------|------|
| `council:design-agent-conversation` | 2 |

## Files Created

| File | Description |
|------|-------------|
| `agents/$WAVE-$NAME.md` | Agent definition |
| `docs/$WAVE-$NAME.md` | Documentation |
| `research/$WAVE-$NAME.md` | Domain research |

## Files Updated

| File | Change |
|------|--------|
| plan context | New agent entry appended |
| `README.md` | Flow diagram updated |
