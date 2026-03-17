---
name: add-agent
description: Add a new agent to the evaluation council
argument-hint: [wave] [name]
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
  - AskUserQuestion
  - Skill
  - Agent
  - WebSearch
  - WebFetch
model: inherit
context: inherit
user-invocable: true
---

# Add Council Agent

Add a new agent to the evaluation council. Runs a focused conversation to design the agent, researches its domain, generates the definition, and creates documentation.

<progress>
- [ ] Step 1: Show roster + select wave
- [ ] Step 2: Design the agent (conversation)
- [ ] Step 3: Research the domain
- [ ] Step 4: Generate agent definition
- [ ] Step 5: Generate documentation
- [ ] Step 6: Update roster docs
</progress>

## Step 1: Show Roster + Select Wave

Glob the agents directory and group by wave:

```
Glob agents/data-*.md → Wave 1 (Data Gathering)
Glob agents/eval-*.md → Wave 2 (Evaluation)
Glob agents/synth-*.md → Wave 3 (Synthesis)
```

For each file, read the frontmatter `name` and `description`.

### If $ARGUMENTS specifies wave and name

Parse `$ARGUMENTS` for wave prefix (data/eval/synth) and name. Store `$WAVE` and `$NAME`. Skip to Step 2 — pass both to the conversation skill so it has context.

### If $ARGUMENTS specifies only a wave

Parse the wave, store `$WAVE`. Skip to Step 2.

### If no arguments

```
AskUserQuestion:
  question: "Which wave should the new agent belong to?"
  header: "Add Agent"
  options:
    - label: "Wave 1 — Data Gathering"
      description: "Gathers raw data from a specific source"
      preview: |
        Current data agents:
        ├─ [name]: [description]
        └─ ...

        Data agents search external sources (GitHub, funding platforms,
        on-chain, web) and write structured findings for evaluators to read.
    - label: "Wave 2 — Evaluation"
      description: "Scores the project on a specific dimension"
      preview: |
        Current eval agents:
        ├─ [name]: [description]
        └─ ...

        Eval agents read ALL data files, then score the project on
        5 dimensions specific to their lens. They never see other
        evaluators' scores.
    - label: "Wave 3 — Synthesis"
      description: "Synthesizes evaluations into a final output"
      preview: |
        Current synth agents:
        └─ [name]: [description]

        Synth agents read ALL evaluations and produce the final report.
        Most councils have a single synth-chair.
```

Store the selected wave as `$WAVE` (data/eval/synth).

## Step 2: Design the Agent (Conversation)

Invoke the agent design conversation sub-skill, passing all available context:

```
<skill name="council:design-agent-conversation" args="$WAVE $NAME" />
```

If `$NAME` was provided in arguments, pass it so the conversation can skip the "what should we call it?" question and focus on dimensions/sources. If only `$WAVE` was provided, pass just the wave type.

This runs a focused conversation scoped to designing a single agent — it won't revisit council-level questions about domain or purpose.

From the conversation, extract:
- `$NAME` — agent name (e.g., `audits`, `governance`, `debate`)
- `$DESCRIPTION` — one-line description
- `$PURPOSE` — detailed purpose
- `$SOURCES` or `$DIMENSIONS` — specific configuration
- `$RESEARCH_NEEDED` — what domain knowledge to gather

The full agent name will be `$WAVE-$NAME` (e.g., `data-audits`, `eval-governance`).

## Step 3: Research the Domain

Create the research directory if it doesn't exist:

```bash
mkdir -p research
```

Spawn a research agent:

```
Agent(
  subagent_type="general-purpose",
  description="Research $WAVE-$NAME",
  prompt="
    Research the domain for council agent $WAVE-$NAME.

    Context from the design conversation:
    - Purpose: $PURPOSE
    - [Sources: $SOURCES | Dimensions: $DIMENSIONS]
    - Research needed: $RESEARCH_NEEDED

    Use WebSearch and WebFetch to find:
    - Best practices for [evaluating/gathering] this domain
    - Available data sources, APIs, scoring methodologies
    - Domain-specific terminology and frameworks

    Write findings to research/$WAVE-$NAME.md with sections:
    - Domain Context (2-3 paragraphs)
    - Data Sources Found (with URLs, access methods)
    - Methodology Notes
    - Key Findings (bullets)
    - Gaps (what couldn't be found)
  "
)
```

Wait for research to complete.

## Step 4: Generate Agent Definition

Determine the template agent filename (resolve before building the prompt):

```
data → $TEMPLATE = "agents/data-github.md"
eval → $TEMPLATE = "agents/eval-technical.md"
synth → $TEMPLATE = "agents/synth-chair.md"
```

If the preferred template doesn't exist (removed during customization), Glob `agents/$WAVE-*.md` and pick the first match. If no agents of that type exist, set `$TEMPLATE = "none"`.

Spawn a generation agent with the **resolved** template path (never pass a literal placeholder):

```
Agent(
  subagent_type="general-purpose",
  description="Generate $WAVE-$NAME",
  prompt="
    Generate the agent definition for $WAVE-$NAME.

    Read these files:
    1. research/$WAVE-$NAME.md — domain research
    2. $TEMPLATE — use as structural template for frontmatter + section layout

    Agent configuration from design:
    - Name: $WAVE-$NAME
    - Description: $DESCRIPTION
    - Purpose: $PURPOSE
    - [Sources: $SOURCES | Dimensions: $DIMENSIONS]

    Write agents/$WAVE-$NAME.md following the exact frontmatter + body
    pattern of the template. Include:
    - Correct frontmatter (name, description, tools matching template)
    - Same section structure as template
    - Specific [sources/dimensions] from the design
    - Domain-appropriate score calibration (for eval agents)
    - $PROJECT, $DATA_DIR/$OUTPUT_DIR variable placeholders

    If no template file was provided, use this structure:
    - Frontmatter: name, description, tools (data agents get WebSearch+WebFetch, eval/synth don't)
    - Sections: title, role description, Input, Process (numbered steps with TaskUpdate + SendMessage), Output Format, edge cases or calibration
  "
)
```

Wait for generation to complete.

## Step 5: Generate Documentation

Spawn a documentation agent:

```
Agent(
  subagent_type="general-purpose",
  description="Document $WAVE-$NAME",
  prompt="
    Generate documentation for agent $WAVE-$NAME.

    Read these files:
    1. agents/$WAVE-$NAME.md — the agent definition
    2. research/$WAVE-$NAME.md — domain context

    Write docs/$WAVE-$NAME.md covering:
    - What this agent does (plain language)
    - [Data sources | Scoring dimensions | Synthesis method]
    - Output location and example structure
    - How to customize it
    - Dependencies (reads from / consumed by)
  "
)
```

Wait for documentation to complete.

## Step 6: Update Roster + Report

Read `README.md` and update the flow diagram to include the new agent in the correct wave.

Show the result:

```
Agent `$WAVE-$NAME` added to Wave [N].

Created:
├─ agents/$WAVE-$NAME.md — agent definition
├─ docs/$WAVE-$NAME.md — documentation
└─ research/$WAVE-$NAME.md — domain research

Updated:
└─ README.md — roster diagram

Run `/council:evaluate <project>` to test the updated council.
```

## Anti-Patterns

- **Never skip the conversation** — even for "obvious" agents, the conversation catches design details
- **Never generate without research** — research produces domain-specific agents, not generic ones
- **Never copy an existing agent and find-replace** — each agent needs its own research and tailored content
- **Never add an agent without documentation** — docs are a first-class artifact
