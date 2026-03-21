# Skill: test-octant

**Invocable:** Yes
**Args:** None
**Tools:** Read, Write, Glob, Grep, Bash, AskUserQuestion, Agent, Task, SendMessage, TaskCreate, TaskUpdate, TaskList, TeamCreate, TeamDelete, WebFetch, WebSearch

## Purpose

Runs the full council evaluation pipeline on 5 hardcoded Octant projects to verify all agents work end-to-end. This is a validation command — it exercises every agent (data, eval, synth) on real projects.

## Test Projects

| Project | Slug | Why |
|---------|------|-----|
| Protocol Guild | `protocol-guild` | Ethereum core contributor funding — strong governance |
| L2BEAT | `l2beat` | L2 analytics — well-known infrastructure |
| growthepie | `growthepie` | L2 ecosystem analytics — growing project |
| Revoke.cash | `revoke-cash` | Token approval management — clear utility |
| Tor Project | `tor-project` | Privacy infrastructure — non-crypto public good |

## Process

| Step | Action | Tools |
|------|--------|-------|
| 1 | Confirm test run — all 5 projects, 1 project, or cancel | AskUserQuestion |
| 2 | Run `/council:evaluate` for each project sequentially | Skill (evaluate) |
| 3 | Validate outputs — check data/eval/synth files exist and are well-formed | Bash, Glob |
| 4 | Report results — summary table with pass/fail per project | — |

## Acceptance Criteria

Per project, validates:
- `council-out/$SLUG/data/` has octant.json, karma.json, social.json, global.json
- `council-out/$SLUG/eval/` has quant.json, qual.json, ostrom-scores.json
- `council-out/$SLUG/synth/` has ostrom-report.md, eas-attestations.json
- REPORT.md exists at slug root

## Part of OptInPG Extension

This skill is part of the OptInPG extension and does not modify any original plugin files.
