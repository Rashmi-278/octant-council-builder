---
description: Evaluate a public goods project using a multi-agent council
argument-hint: <project-name-or-url>
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - Agent
  - Task
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TeamCreate
  - TeamDelete
  - SendMessage
  - WebFetch
  - WebSearch
  - AskUserQuestion
model: opus
context: inherit
user-invocable: true
---

# Public Goods Evaluation Council

Orchestrate a multi-agent council to evaluate a public goods project. Three waves of agents gather data, evaluate from different lenses, and synthesize a final report.

<progress>
- [ ] Step 1: Parse input + discover agents
- [ ] Step 2: Create team + tasks
- [ ] Step 3: Wave 1 — Data Gathering
- [ ] Step 4: Wave 2 — Evaluation
- [ ] Step 5: Wave 3 — Synthesis
- [ ] Step 6: Present report
- [ ] Step 7: Cleanup
</progress>

## Input

`$ARGUMENTS` is the project name or URL to evaluate.

If not provided, AskUserQuestion: "What project should the council evaluate?" with options for well-known projects or free text.

Store as `$PROJECT`. Derive `$SLUG` by lowercasing, replacing spaces/special chars with hyphens, truncating to 40 chars.

## Step 1: Parse Input + Discover Agents

Discover the council roster dynamically from the filesystem:

```
Glob agents/data-*.md → $DATA_AGENTS
Glob agents/eval-*.md → $EVAL_AGENTS
Glob agents/synth-*.md → $SYNTH_AGENTS
```

For each agent file, read the frontmatter `name` and `description` fields.

Create the output directory:
```bash
mkdir -p council-out/$SLUG/data council-out/$SLUG/eval
```

Present the roster to the user:

```
AskUserQuestion:
  question: "Council assembled. Proceed with evaluation?"
  header: "Council"
  options:
    - label: "Run evaluation"
      description: "Start the 3-wave evaluation"
      preview: |
        Project: $PROJECT

        Wave 1 — Data Gathering ($N agents):
        ├─ [name]: [description]
        ├─ [name]: [description]
        └─ ...

        Wave 2 — Evaluation ($M agents):
        ├─ [name]: [description]
        └─ ...

        Wave 3 — Synthesis ($K agents):
        └─ [name]: [description]

        Output: council-out/$SLUG/REPORT.md
    - label: "Modify roster"
      description: "Add or remove agents before running"
```

If "Modify roster" → invoke the `add-agent` skill via the Skill tool, then re-discover.

## Step 2: Create Team + All Tasks

```
TeamCreate(team_name="council-$SLUG", description="Public goods evaluation council for $PROJECT")
```

Pre-create all tasks — one per agent across all three waves:

```
# Wave 1 tasks
TaskCreate(subject="data-github", description="Gather GitHub activity data for $PROJECT")
TaskCreate(subject="data-funding", description="Research funding history for $PROJECT")
... (one per data-* agent)

# Wave 2 tasks
TaskCreate(subject="eval-technical", description="Technical evaluation of $PROJECT")
TaskCreate(subject="eval-community", description="Community evaluation of $PROJECT")
... (one per eval-* agent)

# Wave 3 tasks
TaskCreate(subject="synth-chair", description="Synthesize final council report for $PROJECT")
... (one per synth-* agent)
```

## Step 3: Wave 1 — Data Gathering

Spawn ALL data agents in a **single message** for true parallelism:

```
Task(
  name="w1-github",
  subagent_type="general-purpose",
  team_name="council-$SLUG",
  model="sonnet",
  run_in_background=true,
  prompt="
    You are a data-gathering agent on a public goods evaluation council.

    [INSERT FULL CONTENTS OF agents/data-github.md BODY HERE]

    PROJECT: $PROJECT
    OUTPUT_DIR: council-out/$SLUG/data
    TASK_SUBJECT: data-github

    Begin by claiming your task, then gather data, write output, complete task, and send summary.
  "
)
Task(
  name="w1-funding",
  ...same pattern with agents/data-funding.md...
)
... (one Task() per data-* agent, ALL in the same message)
```

**Wave gate:** After spawning, poll `TaskList` until ALL Wave 1 tasks show `status="completed"`. Do not proceed until the gate clears.

After Wave 1 completes, briefly note to the user: "Wave 1 complete — N data sources gathered."

## Step 4: Wave 2 — Evaluation

Spawn ALL eval agents in a **single message**:

```
Task(
  name="w2-technical",
  subagent_type="general-purpose",
  team_name="council-$SLUG",
  model="sonnet",
  run_in_background=true,
  prompt="
    You are an evaluator on a public goods evaluation council.

    [INSERT FULL CONTENTS OF agents/eval-technical.md BODY HERE]

    PROJECT: $PROJECT
    DATA_DIR: council-out/$SLUG/data
    OUTPUT_DIR: council-out/$SLUG/eval
    TASK_SUBJECT: eval-technical

    Begin by claiming your task, then read ALL data files, score, write evaluation, complete task, and send summary.
  "
)
... (one Task() per eval-* agent, ALL in the same message)
```

**Wave gate:** Poll `TaskList` until ALL Wave 2 tasks show `status="completed"`.

After Wave 2 completes, briefly note: "Wave 2 complete — N evaluations filed."

## Step 5: Wave 3 — Synthesis

Spawn synth agent(s):

```
Task(
  name="w3-chair",
  subagent_type="general-purpose",
  team_name="council-$SLUG",
  model="opus",
  run_in_background=true,
  prompt="
    You are the chair of a public goods evaluation council.

    [INSERT FULL CONTENTS OF agents/synth-chair.md BODY HERE]

    PROJECT: $PROJECT
    EVAL_DIR: council-out/$SLUG/eval
    OUTPUT_PATH: council-out/$SLUG/REPORT.md
    TASK_SUBJECT: synth-chair

    Begin by claiming your task, then read ALL evaluations, synthesize, write report, complete task, and send summary.
  "
)
```

**Wave gate:** Poll `TaskList` until synth task shows `status="completed"`.

## Step 6: Present Report

Read `council-out/$SLUG/REPORT.md` and present to the user:

```
AskUserQuestion:
  question: "Council report complete. What next?"
  header: "Report"
  options:
    - label: "Done"
      description: "Accept the report"
      preview: |
        [Show the full REPORT.md content as preview]
    - label: "Evaluate another project"
      description: "Run the council on a different project"
    - label: "Dig deeper"
      description: "Ask a specific evaluator to expand their assessment"
```

If "Evaluate another" → ask for new project name, loop back to Step 1.
If "Dig deeper" → ask which evaluator, spawn a single follow-up agent with targeted questions.

## Step 7: Cleanup

```
SendMessage(type="shutdown_request", recipient="broadcast", content="Evaluation complete. Shutting down council.")
TeamDelete(team_name="council-$SLUG")
```

Report to user:
- Report saved at `council-out/$SLUG/REPORT.md`
- Data files at `council-out/$SLUG/data/`
- Evaluation files at `council-out/$SLUG/eval/`

## Anti-Patterns

- **Never skip the wave gate** — all agents in a wave must complete before the next wave starts
- **Never let evaluators see each other's scores** — independence is the whole point
- **Never fabricate data** — if an agent can't find information, it says so
- **Never spawn agents one at a time** — all agents in a wave go in a single message for parallelism
- **Never synthesize yourself** — the chair agent does synthesis, not the orchestrator
