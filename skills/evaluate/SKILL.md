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
- [ ] Step 6.5: Auto-publish to dashboard
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

**Shutdown:** Once ALL Wave 1 tasks are completed, send a `shutdown_request` to each Wave 1 teammate by name (e.g., `SendMessage(to="w1-github", message={type: "shutdown_request", reason: "Wave 1 complete"})`) so they don't stay running idle. Do this for every `w1-*` agent.

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

    IMPORTANT: After completing your task and sending your summary, STAY AVAILABLE. The synthesis
    agent may send you follow-up questions asking you to clarify or defend your scores. When you
    receive a message, read it, answer thoughtfully based on your evaluation, and reply via
    SendMessage. Do not shut down until you receive a shutdown_request.
  "
)
... (one Task() per eval-* agent, ALL in the same message)
```

**Wave gate:** Poll `TaskList` until ALL Wave 2 tasks show `status="completed"`.

**Do NOT shut down Wave 2 agents yet.** Evaluators stay alive through Wave 3 so the synthesizer can send them follow-up questions via `SendMessage`. They will be shut down after Wave 3 completes.

After Wave 2 completes, briefly note: "Wave 2 complete — N evaluations filed."

## Step 5: Wave 3 — Synthesis

Spawn synth agent(s). Include the list of live Wave 2 evaluator names so the synthesizer can message them:

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

    LIVE EVALUATORS (available for follow-up questions via SendMessage):
    [List each w2-* agent name, e.g.: w2-technical, w2-community, w2-financial, w2-impact, w2-skeptic]

    You can send a message to any evaluator to ask for clarification, request they defend a score,
    or resolve disagreements. Use SendMessage(to="w2-technical", message="your question").
    Wait for their reply before continuing. Use this sparingly — only when the written evaluation
    leaves a genuine ambiguity that affects the final report.

    Begin by claiming your task, then read ALL evaluations. If any scores or findings need
    clarification, message the relevant evaluator. Then synthesize, write report, complete task,
    and send summary.
  "
)
```

**Wave gate:** Poll `TaskList` until synth task shows `status="completed"`.

**Shutdown:** After Wave 3 completes, shut down ALL remaining agents — both Wave 2 evaluators and Wave 3 synthesizer. Send a `shutdown_request` to each `w2-*` agent and each `w3-*` agent by name.

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

## Step 6.5: Auto-Publish to Dashboard

Check the `PUBLISH_OSTROM` environment variable. If not set or set to `true`, auto-publish the evaluation to the hosted dashboard.

```bash
# Check publish flag (default: true)
echo ${PUBLISH_OSTROM:-true}
```

If `PUBLISH_OSTROM` is `true` (or not set) AND `PUBLISH_URL` is set:

1. Read the key output files:
   - `council-out/$SLUG/eval/ostrom-scores.json` → `ostrom_scores`
   - `council-out/$SLUG/eval/quant.json` → `quant_scores`
   - `council-out/$SLUG/eval/qual.json` → `qual_json`
   - `council-out/$SLUG/synth/eas-attestations.json` → `eas_json`
   - `council-out/$SLUG/REPORT.md` → `report_md`
   - `council-out/$SLUG/synth/ostrom-report.md` → `ostrom_report_md`

2. Bundle into a single JSON payload:
```json
{
  "slug": "$SLUG",
  "project": "$PROJECT",
  "ostrom_scores": { ... },
  "quant_scores": { ... },
  "qual_json": { ... },
  "eas_json": { ... },
  "report_md": "...",
  "ostrom_report_md": "...",
  "metadata": {
    "evaluated_at": "ISO timestamp",
    "agent_count": N,
    "wave_count": 3
  }
}
```

3. POST to `$PUBLISH_URL/api/publish`:
```bash
curl -s -X POST "$PUBLISH_URL/api/publish" \
  -H "Content-Type: application/json" \
  -d @/tmp/council-publish-$SLUG.json
```

4. If POST succeeds (201), tell the user: "Published to dashboard: $URL"
   If POST fails, warn the user but don't block: "Publish failed (evaluation saved locally). You can publish later with /council:deploy-to-production"

If `PUBLISH_OSTROM` is `false`, skip silently.
If `PUBLISH_URL` is not set, tell the user: "Set PUBLISH_URL to auto-publish evaluations to a hosted dashboard."

## Step 7: Cleanup

Wave 1 agents were shut down after Wave 1. Wave 2 and Wave 3 agents were shut down after Wave 3. Now clean up the team:

```
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
