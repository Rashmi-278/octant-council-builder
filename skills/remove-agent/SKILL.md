---
name: remove-agent
description: Remove an agent from the evaluation council
argument-hint: [agent-name]
allowed-tools:
  - Read
  - Glob
  - Bash
  - AskUserQuestion
model: inherit
context: inherit
user-invocable: true
---

# Remove Council Agent

Remove an agent from the evaluation council. Deletes the agent definition, its documentation, and updates the council plan if one exists.

## Step 1: Discover Roster

Glob the agents directory and group by wave:

```
Glob agents/data-*.md → Wave 1 (Data Gathering)
Glob agents/eval-*.md → Wave 2 (Evaluation)
Glob agents/synth-*.md → Wave 3 (Synthesis)
```

For each file, read the frontmatter `name` and `description`.

### If $ARGUMENTS provided

Check if `agents/$ARGUMENTS.md` exists. If yes, skip to Step 2 with that agent pre-selected. If no, show the roster and ask.

### If no argument

Present the roster and ask which agent to remove:

```
AskUserQuestion:
  question: "Which agent should be removed?"
  header: "Remove Agent"
  options:
    [One option per agent, grouped by wave]:
    - label: "[name]"
      description: "Wave N — [description]"
      preview: |
        File: agents/[name].md
        Wave: [N] — [Data Gathering | Evaluation | Synthesis]
        Role: [description]

        Removing this agent means the council will no longer:
        [1-line summary of what will be lost]
```

Store the selected agent as `$AGENT`.

## Step 2: Last-Agent Guard

Before confirming, check if this is the last agent of its wave type:

```
Glob agents/$PREFIX-*.md → count agents of same type
```

If this is the **last synth agent**, show a hard warning:

```
AskUserQuestion:
  question: "This is the only synthesis agent. Removing it means the council will produce NO final report. Continue?"
  header: "Warning"
  options:
    - label: "Remove anyway"
      description: "I'll add a replacement later"
    - label: "Cancel"
      description: "Keep the agent"
```

If "Cancel" → stop, report "No changes made."

If this is the **last data agent** or **last eval agent**, show a softer warning in the confirmation (Step 3) noting that the wave will be empty.

## Step 3: Confirm with Impact Preview

Read the agent file to understand its role, then confirm:

```
AskUserQuestion:
  question: "Confirm removal of $AGENT?"
  header: "Confirm"
  options:
    - label: "Remove"
      description: "Delete agent and documentation"
      preview: |
        Removing: $AGENT
        Wave: [N] — agents remaining: [M-1]

        Impact:
        - The council will no longer assess: [what this agent evaluates/gathers]
        - [Wave-specific impact]:
          - Data agent: evaluators will have less data to work with
          - Eval agent: the synthesis will have fewer perspectives
          - Synth agent: the council output format will change

        Files to delete:
        - agents/$AGENT.md
        - docs/$AGENT.md (if exists)
    - label: "Cancel"
      description: "Keep the agent"
```

If "Cancel" → stop, report "No changes made."

## Step 4: Delete Files

```bash
rm agents/$AGENT.md
```

Check if documentation exists and delete:
```
Glob docs/$AGENT.md → if found, rm docs/$AGENT.md
```

Check if research exists and delete:
```
Glob research/$AGENT.md → if found, rm research/$AGENT.md
```

## Step 5: Show Updated Roster

Glob agents again to show the current roster:

```
Updated council roster:

Wave 1 — Data Gathering (N agents):
├─ [name]: [description]
└─ ...

Wave 2 — Evaluation (M agents):
├─ [name]: [description]
└─ ...

Wave 3 — Synthesis (K agents):
└─ [name]: [description]

Agent "$AGENT" removed. Run `/council:evaluate <project>` to test the updated council.
```
