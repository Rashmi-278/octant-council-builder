---
name: design
description: Design your evaluation council — domain, agents, lenses, data sources
argument-hint: [domain]
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
  - AskUserQuestion
  - Skill
  - EnterPlanMode
  - ExitPlanMode
  - Agent
  - WebSearch
  - WebFetch
model: opus
context: inherit
user-invocable: true
---

# Council Design — Design Your Evaluation Council

A planning skill that guides the user through designing a custom evaluation council. Two phases: conversational discovery → structured design → plan, then implementation via research/generate/document agents.

Plan mode handles the plan file natively — no manual file writing needed.

<progress>
- [ ] Step 1: Enter plan mode
- [ ] Step 2: Dream extraction (conversation)
- [ ] Step 3: Propose agent roster (structured questions)
- [ ] Step 4: Per-agent configuration (structured questions)
- [ ] Step 5: Architecture confirmation + exit plan mode
- [ ] Step 6: Implementation (post-approval)
</progress>

## Step 1: Enter Plan Mode

```
EnterPlanMode
```

## Step 2: Dream Extraction

If `$ARGUMENTS` is empty, ask first:

```
AskUserQuestion:
  question: "What domain should this council evaluate?"
  header: "Council Domain"
  options:
    - label: "Public goods projects"
      description: "General-purpose evaluation for funding decisions"
    - label: "DeFi protocols"
      description: "Evaluate DeFi projects on security, TVL, governance"
    - label: "L2 rollups"
      description: "Evaluate Layer 2 scaling solutions"
    - label: "Research grants"
      description: "Evaluate academic/applied research proposals"
    - label: "Other"
      description: "Describe your domain"
```

Store the answer as `$DOMAIN`. If "Other", use a follow-up text question.

Invoke the conversation sub-skill:

```
<skill name="council:design-conversation" args="$DOMAIN" />
```

(If `$ARGUMENTS` was provided, use it directly as the args.)

This runs a pure conversational dialogue — no structured questions, no tools. It returns a summary with:
- **Domain** — what we're evaluating
- **Purpose** — what decision this informs
- **Data priorities** — top data sources
- **Evaluation priorities** — the lenses that matter
- **Skeptic focus** — domain-specific red flags
- **Out of scope** — what the council won't assess
- **Core essence** — the ONE non-negotiable

Store these as context for the structured phase.

## Step 3: Propose Agent Roster

Based on the conversation, propose a default agent roster. First discover what already exists on disk, then present a proposed roster for approval.

### Discover existing agents

```
Glob agents/data-*.md → existing data agents
Glob agents/eval-*.md → existing eval agents
Glob agents/synth-*.md → existing synth agents
```

Read each agent's frontmatter to get name + description. These are the "existing" agents — they already have definitions and don't need research/generation.

### Q1: Data sources

Present the proposed roster as a single confirmation. Include all existing data agents plus any domain-specific suggestions from the conversation:

```
AskUserQuestion:
  question: "Here's the proposed data-gathering roster. Any changes?"
  header: "Wave 1 — Data Gathering"
  options:
    - label: "Looks good"
      description: "Keep this roster"
      preview: |
        Proposed data agents:
        ├─ data-github: GitHub activity, contributors, maintenance (existing)
        ├─ data-web: Website, docs, team, communications (existing)
        ├─ data-funding: Funding history from Gitcoin/RetroPGF/etc (existing)
        ├─ data-onchain: Contracts, TVL, users, on-chain metrics (existing)
        [├─ data-{suggestion}: {description} (NEW — from conversation)]
        └─ ...
    - label: "Add an agent"
      description: "I need a data source not listed here"
    - label: "Remove an agent"
      description: "Drop one of the listed agents"
```

If "Add" → ask: "What data source should this agent search? Give it a name (e.g., 'audits', 'discourse', 'l2beat')." Add to the roster, re-present Q1.
If "Remove" → ask which one. Remove from roster, re-present Q1.
If "Looks good" → store `$DATA_AGENTS` and proceed.

### Q2: Evaluation lenses

Same pattern — present existing eval agents plus conversation-driven suggestions:

```
AskUserQuestion:
  question: "Here's the proposed evaluation roster. Any changes?"
  header: "Wave 2 — Evaluation"
  options:
    - label: "Looks good"
      description: "Keep this roster"
      preview: |
        Proposed eval agents:
        ├─ eval-technical: Code quality, maintenance, contributor health (existing)
        ├─ eval-community: Users, governance, ecosystem integration (existing)
        ├─ eval-financial: Funding diversity, sustainability, efficiency (existing)
        ├─ eval-impact: Public goods properties, counterfactual impact (existing)
        ├─ eval-skeptic: Red flags, gaming vectors, reasons NOT to fund (existing)
        [├─ eval-{suggestion}: {description} (NEW — from conversation)]
        └─ ...
    - label: "Add an agent"
      description: "I need an evaluation lens not listed here"
    - label: "Remove an agent"
      description: "Drop one of the listed agents"
```

Same add/remove/confirm loop. Store `$EVAL_AGENTS`.

### Q3: Synthesis approach

```
AskUserQuestion:
  question: "How should evaluations be synthesized into a final output?"
  header: "Wave 3 — Synthesis"
  options:
    - label: "Single chair"
      description: "One synthesizer produces a unified report with recommendation"
      preview: |
        Keeps: synth-chair (existing)
        Creates: nothing new

        The default approach. A single synth-chair agent reads all evaluations
        and produces a score card, areas of agreement/disagreement, key risk,
        and a FUND / FUND WITH CONDITIONS / DON'T FUND recommendation.
    - label: "Debate format"
      description: "Bull and bear synthesizers argue, then a chair decides"
      preview: |
        Keeps: synth-chair (existing — becomes the final arbiter)
        Creates: synth-bull (NEW), synth-bear (NEW)

        Three synth agents: synth-bull (strongest case FOR), synth-bear
        (strongest case AGAINST), and synth-chair (weighs both arguments
        and renders verdict). More nuanced but slower.

        Wave 3 runs in two sub-waves:
        3a: synth-bull + synth-bear (parallel) → write to council-out/$SLUG/synth/
        3b: synth-chair reads both arguments + all evaluations → writes REPORT.md

        NOTE: The generated synth-chair for debate format will self-sequence —
        it polls TaskList for bull + bear completion before synthesizing.
    - label: "Ranked comparison"
      description: "Compare the evaluated project against alternatives"
      preview: |
        Removes: synth-chair (replaced)
        Creates: synth-ranker (NEW)

        A synth-ranker agent places the project in context of similar
        projects in the domain. Useful when evaluating multiple projects
        for a limited funding pool.
```

Store selections as `$DATA_AGENTS`, `$EVAL_AGENTS`, `$SYNTH_APPROACH`.

## Step 4: Per-Agent Configuration

For each selected agent, ask targeted questions to configure dimensions and sources. Batch by wave.

### Data agents (single batched AskUserQuestion)

For each NEW data agent (not one already discovered on disk in Step 3):

```
AskUserQuestion:
  question: "What specific sources should data-[name] search?"
  header: "Configure: data-[name]"
  type: text
  placeholder: "e.g., specific APIs, websites, databases, search queries"
```

### Eval agents (single batched AskUserQuestion)

For each NEW eval agent (not one already discovered on disk in Step 3):

```
AskUserQuestion:
  question: "What 5 scoring dimensions should eval-[name] use?"
  header: "Configure: eval-[name]"
  type: text
  placeholder: "e.g., 'Validator diversity, Token distribution, Upgrade mechanism, Governance participation, MEV resistance'"
```

For existing agents (discovered in Step 3), skip — their definitions are already written.

### Synth agents (if non-default approach)

If the user chose "Debate format" in Q3, three synth agents are needed: `synth-bull`, `synth-bear`, and `synth-chair`. The existing `synth-chair` can be kept as-is. For the new ones:

```
AskUserQuestion:
  question: "For the debate format — what makes a strong case FOR funding in this domain?"
  header: "Configure: synth-bull"
  type: text
  placeholder: "e.g., 'Emphasize growth metrics, community adoption, technical innovation, and ecosystem value'"
```

```
AskUserQuestion:
  question: "What makes a strong case AGAINST funding? What should the bear advocate focus on?"
  header: "Configure: synth-bear"
  type: text
  placeholder: "e.g., 'Emphasize sustainability risks, competition, team concerns, and alternative allocation'"
```

If the user chose "Ranked comparison", one new agent is needed: `synth-ranker`. The existing `synth-chair` is replaced:

```
AskUserQuestion:
  question: "What projects or benchmarks should the ranker compare against?"
  header: "Configure: synth-ranker"
  type: text
  placeholder: "e.g., 'Compare against top 5 projects in the same category by TVL, users, and funding received'"
```

Note: "Ranked comparison" replaces synth-chair. Mark `synth-chair` for removal in the plan.

## Step 5: Architecture Confirmation

Present the complete plan for approval:

```
AskUserQuestion:
  question: "Council design complete. Review and approve?"
  header: "Council Design"
  options:
    - label: "Approve plan"
      description: "Proceed to implementation"
      preview: |
        ┌─ COUNCIL DESIGN ────────────────────────┐
        │ Domain: [domain from conversation]       │
        │ Purpose: [purpose from conversation]     │
        └──────────────────────────────────────────┘

        Wave 1 — Data Gathering ([N] agents):
        ├─ [name]: [what it fetches]
        ├─ [name]: [what it fetches]
        └─ ...

        Wave 2 — Evaluation ([M] agents):
        ├─ [name]: [lens] — [5 dimensions]
        ├─ [name]: [lens] — [5 dimensions]
        └─ ...

        Wave 3 — Synthesis ([K] agents):
        └─ [name]: [output format]

        Implementation steps:
        1. Research each NEW agent's domain ([P] agents to research)
        2. Generate agent definitions from research ([P] agents to create)
        3. Generate per-agent documentation ([P] new docs)
        4. Update evaluate skill + README

        Existing agents to keep: [list defaults being reused]
        Existing agents to remove: [list defaults not selected]
        New agents to create: [list new agents]

        Estimated artifacts:
        ├─ research/{name}.md × [P]
        ├─ agents/{name}.md × [P new]
        ├─ docs/{name}.md × [P new]
        └─ Updated: README.md
    - label: "Revise"
      description: "Go back and change selections"
    - label: "Cancel"
      description: "Discard and exit"
```

If "Revise" → loop back to Step 3.
If "Cancel" → ExitPlanMode, report "Council design cancelled."

## Step 5 (continued): Exit Plan Mode

After approval:

```
ExitPlanMode
```

The plan file is written automatically by plan mode. Present to the user:

```
Council design complete.

Review the plan, then approve to begin implementation. Implementation will:
1. Research [P] new agent domains (parallel)
2. Generate [P] agent definitions (parallel)
3. Generate [P] documentation pages (parallel)
4. Remove [R] deselected agents
5. Update README
```

## Step 6: Implementation (Post-Approval)

**STOP HERE.** Do not proceed until the user explicitly approves (e.g., "approve", "go", "looks good", "implement it"). If the user wants changes, re-enter plan mode and revise. If the user says nothing related to approval, ask:

```
AskUserQuestion:
  question: "Ready to implement the council design?"
  header: "Implement"
  options:
    - label: "Implement now"
      description: "Research, generate, and document all new agents"
    - label: "Let me review first"
      description: "I'll read the plan and get back to you"
    - label: "Cancel"
      description: "Discard the plan"
```

If "Let me review" → stop and wait for the user to come back.
If "Cancel" → report "Council design cancelled."

After the user approves, execute the plan:

### 6a: Research wave (parallel)

Use the plan content from the conversation context to find all agents with `Status: new`.

```bash
mkdir -p research
```

For each NEW agent, spawn a research agent in the background:

```
Agent(
  subagent_type="general-purpose",
  run_in_background=true,
  description="Research [agent-name]",
  prompt="
    You are researching the domain for a council agent.

    Agent: [agent-name]
    Purpose: [purpose from plan]
    Research needed: [research brief from plan]

    Research the domain using WebSearch and WebFetch:
    - Best practices for [evaluating/gathering] [domain]
    - Available data sources, APIs, scoring methodologies

    Write findings to research/[agent-name].md with sections:
    - Domain Context (2-3 paragraphs)
    - Data Sources Found (with URLs, access methods)
    - Methodology Notes
    - Key Findings (bullets)
    - Gaps (what couldn't be found)
  "
)
```

Spawn ALL research agents in a **single message** for parallelism. Wait for all to complete.

### 6b: Generate wave (parallel)

For each NEW agent, determine its template file from the prefix:
- `data-*` → use `agents/data-github.md` as template (if it exists)
- `eval-*` → use `agents/eval-technical.md` as template (if it exists)
- `synth-*` → use `agents/synth-chair.md` as template (if it exists)

If the template doesn't exist (all agents of that type were removed), pick any remaining agent of the same type, or fall back to detailed instructions in the prompt.

Spawn a generation agent for each:

```
Agent(
  subagent_type="general-purpose",
  run_in_background=true,
  description="Generate [agent-name]",
  prompt="
    Generate the agent definition for [agent-name].

    Read these files:
    1. research/[agent-name].md — domain expertise from research
    2. agents/[SPECIFIC-TEMPLATE-FILENAME].md — use as structural template

    Agent config from plan:
    - Purpose: [purpose]
    - Dimensions/Sources: [dimensions or sources]
    - Status: new

    Write the agent definition to agents/[agent-name].md following the
    exact frontmatter + body pattern of the template:

    Frontmatter must have: name, description, tools (matching template's tool list).

    Body structure for data agents: title, role description, Input ($PROJECT, $OUTPUT_DIR),
    Process (TaskUpdate claim → search/fetch → normalize → write → TaskUpdate complete →
    SendMessage), Output Format (markdown template with tables), edge cases.

    Body structure for eval agents: title, role description, Input ($PROJECT, $DATA_DIR,
    $OUTPUT_DIR), Process (TaskUpdate claim → read data → score 5 dimensions → composite →
    write → TaskUpdate complete → SendMessage), Scoring table, Output Format, Score calibration
    (9-10 exceptional / 7-8 strong / 5-6 adequate / 3-4 weak / 1-2 critical).

    Body structure for synth agents: title, role description, Input ($PROJECT, $EVAL_DIR,
    $OUTPUT_PATH), Process (TaskUpdate claim → read evals → extract scores → find
    agreement/disagreement → synthesize → write → TaskUpdate complete → SendMessage),
    Output Format, Decision criteria.
  "
)
```

Spawn ALL in a single message. Wait for all to complete.

### 6c: Documentation wave (parallel)

For each NEW agent, spawn a doc agent:

```
Agent(
  subagent_type="general-purpose",
  run_in_background=true,
  description="Document [agent-name]",
  prompt="
    Generate documentation for agent [agent-name].

    Read these files:
    1. agents/[agent-name].md — the agent definition
    2. research/[agent-name].md — domain context

    Write docs/[agent-name].md covering:
    - What this agent does (plain language)
    - Data sources or scoring dimensions (with details)
    - Output location and structure
    - How to customize it
    - Dependencies (what it reads from, what consumes its output)
  "
)
```

Spawn ALL in a single message. Wait for all to complete.

### 6d: Remove deselected agents

From the plan context, find agents marked for removal. For each:

```bash
rm agents/[agent-name].md
rm docs/[agent-name].md  # if exists
```

### 6e: Update README

Read `README.md` and update:
- The architecture diagram (Wave 1/2/3 agent lists)
- The agent discovery table
- The fork ideas table

### 6f: Report

```
Council implementation complete.

Created:
├─ research/*.md — [P] research files
├─ agents/*.md — [P] new agent definitions
├─ docs/*.md — [P] documentation pages
├─ Updated README.md

Removed:
├─ [R] deselected default agents

Run `/council:evaluate <project>` to test your configured council.
```

## Anti-Patterns

- **Never skip the conversation** — structured questions alone miss domain nuance
- **Never generate agents without research** — research makes the difference between generic and domain-specific
- **Never spawn agents sequentially** — all agents in a wave go in a single message for parallelism
- **Never modify existing agent definitions** — only create new ones and remove deselected ones
