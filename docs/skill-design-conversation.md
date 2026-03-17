# Skill: design-conversation

**Invocable:** No (called by `council:design`)
**Args:** `[domain]` (e.g. `"DeFi protocols"`)
**Tools:** Read, Write

## Purpose

Pure conversational dialogue to extract the user's vision for an evaluation council. Thinking partner, not interviewer. Returns a structured summary consumed by the parent skill's roster design phase.

## Stop Conditions

Conversation ends when all 7 can be answered:

| # | Question |
|---|----------|
| 1 | What domain are we evaluating? |
| 2 | What decision does this council inform? |
| 3 | What data sources can be fetched and measured? |
| 4 | What evaluation lenses define "good" in this domain? |
| 5 | What are the domain-specific red flags? |
| 6 | What is out of scope? |
| 7 | What is the ONE non-negotiable criterion? |

## Exit Summary

```
**Domain:** ...
**Purpose:** ...
**Data priorities:** ...
**Evaluation priorities:** ...
**Skeptic focus:** ...
**Out of scope:** ...
**Core essence:** ...
```

## Approach

- Follow user's energy, not a checklist
- Challenge vagueness: "impact" → impact on whom, measured how, over what timeframe?
- Single-word answers get pushed back
- No premature agent design
- No structured questions — pure conversation
