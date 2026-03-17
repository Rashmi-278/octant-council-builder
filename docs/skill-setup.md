# Skill: setup

**Invocable:** Yes
**Args:** None
**Tools:** Bash, AskUserQuestion

## Purpose

Installs the council plugin for hackathon participants. Adds a shell alias and enables the agent teams feature. Explains everything before making changes.

## What It Does

Before touching anything, the skill explains exactly what will change:

1. **Shell alias** — so the user can launch `claude --plugin-dir <path>` with a short command
2. **Teams env var** — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, required by the evaluate skill's parallel agent waves

Both lines are tagged with `# public-goods-council` for clean removal/update.

## Process

| Step | Action |
|------|--------|
| 1 | Detect shell (`$SHELL`), config file, plugin directory |
| 2 | Explain both changes (alias + teams env var) and ask to proceed |
| 3 | Ask for alias name (text input) |
| 4 | Validate: non-empty, alphanumeric, not already taken |
| 5 | Remove any existing tagged lines, append new alias + env var |
| 6 | Report: what was added, how to activate, what to try |

## Lines Added to Shell Config

```bash
# zsh/bash
alias council='claude --plugin-dir "/path/to/repo"'  # public-goods-council
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1  # public-goods-council

# fish
alias council "claude --plugin-dir '/path/to/repo'"  # public-goods-council
set -gx CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1  # public-goods-council
```

## Re-run Safety

Tagged with `# public-goods-council`. Re-running removes old lines before writing new ones.

## Why Teams?

The `council:evaluate` skill uses `TeamCreate` to coordinate parallel agent waves. Without `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, the TeamCreate tool is unavailable and evaluation will fail.
