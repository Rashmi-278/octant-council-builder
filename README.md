# Council Builder

A Claude Code plugin that **generates multi-agent evaluation councils**. It is not a council — it's a tool for building one. The default agents ship as a starting point for the [Octant hackathon](https://synthesis.md/hack/#octant), but they're scaffolding, not a finished product. Your job is to run `/council:setup`, reshape the agents, and make something that actually evaluates well for your domain.

Out of the box this does nothing useful. It needs your TLC to become a real evaluation tool.

## How it works

You design a council through conversation. The plugin then researches your domain, generates specialized agents, and wires them into a three-wave execution pattern:

```
Wave 1 — Data (parallel)        Wave 2 — Eval (parallel)       Wave 3 — Synth
┌──────────────────────┐        ┌──────────────────────┐       ┌──────────────────────┐
│ your data agents     │        │ your eval agents     │       │ your synth agent(s)  │
│ gather raw info      │───────▶│ score independently  │──────▶│ synthesize verdict   │
│ from external sources│        │ never see each other │       │ → REPORT.md          │
└──────────────────────┘        └──────────────────────┘       └──────────────────────┘
```

Evaluators never see each other's scores. That's the point — independence prevents groupthink. The synthesizer *can* talk back to evaluators via team tools — asking clarifying questions, challenging scores, or requesting deeper analysis before writing the final report.

## Get started

```bash
# 1. Settings (one time — enables Claude teams + creates shell alias)
/council:settings

# 2. Try the default scaffold on a real project to see the pattern
/council:evaluate Aave DAO

# 3. Now make it yours — this is the real step
/council:setup DeFi lending protocols
/council:setup climate impact DAOs
/council:setup developer tooling grants
```

Step 3 is where the work happens. `/council:setup` runs a conversation to understand your domain, proposes an agent roster, researches each agent's domain, and generates the definitions. The council you end up with is yours.

## Skills

| Skill | Purpose |
|-------|---------|
| `/council:settings` | Install shell alias for this plugin |
| `/council:setup [domain]` | **Design your council** — conversation → roster → research → generate |
| `/council:evaluate <project>` | Run the council on a project |
| `/council:add-agent` | Add a single agent via conversation → research → generate |
| `/council:remove-agent` | Remove an agent with impact preview |

## What you can change

**Everything.** The plugin is a council *factory*, not a council.

- **`/council:setup`** — redesign the entire council for a new domain. New agents, new dimensions, new data sources.
- **`/council:add-agent`** / **`/council:remove-agent`** — tune the roster one agent at a time.
- **Edit agents directly** — every agent is a markdown file in `agents/`. Change scoring dimensions, data sources, calibration. The orchestrator discovers agents by filename prefix, no config to update.
- **Change the output** — modify agent templates to produce JSON, comparison matrices, grant proposals, whatever.

## Agent discovery

| Prefix | Wave | Role |
|--------|------|------|
| `agents/data-*.md` | 1 | Gather raw data from external sources |
| `agents/eval-*.md` | 2 | Score project on 5 dimensions (1-10) |
| `agents/synth-*.md` | 3 | Synthesize evaluations into report |

Add agent = create markdown file with right prefix. Remove agent = delete the file. No registry.

## Output

```
council-out/{slug}/
├── data/           ← Wave 1 output (one .md per data agent)
├── eval/           ← Wave 2 output (one .md per eval agent)
└── REPORT.md       ← Wave 3 output (final verdict)
```

## Synthesis approaches

| Approach | Agents | How it works |
|----------|--------|-------------|
| Single chair (default) | `synth-chair` | Reads all evals, produces unified report |
| Debate | `synth-bull` + `synth-bear` + `synth-chair` | Bull argues FOR, bear AGAINST, chair decides |
| Ranked | `synth-ranker` (replaces chair) | Compares project against alternatives |

Configure via `/council:setup`.

## Sharing your council

This is a Claude Code plugin — a repo with `.claude-plugin/plugin.json` and some markdown files. Once you design your own council via `/council:setup`, anyone can install it:

1. Push your fork
2. Share the repo URL
3. They paste this into Claude Code (replacing the URL with yours):
   ```
   fetch https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/SKILL.md and follow the instructions
   ```

No packaging, no publishing, no registry. A council is just a repo. Fork it, redesign the agents, push it, share the URL.

## Domain ideas

| Domain | Swap/add | Why |
|--------|----------|-----|
| DeFi | `data-audits`, `eval-security` | Security and audit trail matter |
| L2 rollups | `data-l2beat`, `eval-decentralization` | L2Beat has the data |
| Grants | `data-milestones`, `eval-delivery` | Track record of shipping |
| Research | `data-papers`, `eval-novelty` | Academic rigor |

The execution harness (orchestrator + wave pattern) stays the same. Swap agents for your domain.

---

### OptInPG Public Goods Extension (optional)

**Live dashboard:** [optinpg-ostrom.netlify.app](https://optinpg-ostrom.netlify.app/)
**Documentation:** [rashmi-278.github.io/octant-council-builder](https://rashmi-278.github.io/octant-council-builder/)

Adds Octant-native data sources, Elinor Ostrom's 8 Rules scoring, and EAS on-chain attestations. Zero changes to the original plugin.

```bash
# Evaluate a project with Ostrom scoring (agents auto-discovered)
/council:evaluate Protocol Guild

# Deploy the dashboard to production
/council:deploy-to-production protocol-guild
```

See `PRD.md` for full details. Agents: `data-octant-scraper`, `data-karma`, `data-social-indexer`, `data-global-sources`, `eval-quantitative`, `eval-qualitative`, `eval-ostrom`, `synth-ostrom-report`, `synth-eas-attestation`.
