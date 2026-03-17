---
name: setup
description: Install the council plugin — shell alias + teams feature + permissions
allowed-tools:
  - Bash
  - AskUserQuestion
model: inherit
context: inherit
user-invocable: true
---

# Council Setup

Sets up the council plugin for a hackathon participant. Before doing anything, explains everything that will happen and asks for confirmation.

<progress>
- [ ] Step 1: Detect environment
- [ ] Step 2: Explain what setup will do
- [ ] Step 3: Ask for alias name
- [ ] Step 4: Validate alias is available
- [ ] Step 5: Write alias + env var to shell config
- [ ] Step 6: Report success
</progress>

## Step 1: Detect Environment

Resolve the plugin directory:

```bash
PLUGIN_DIR="$(cd "$(dirname "$(find . -path './skills/setup/SKILL.md' -maxdepth 3)")/../../" && pwd)"
```

Detect shell and config file:

```bash
echo "SHELL=$SHELL"
```

Map shell to config:
- `zsh` → `~/.zshrc`
- `bash` → `~/.bashrc` (or `~/.bash_profile` on macOS if `.bashrc` doesn't exist)
- `fish` → `~/.config/fish/config.fish`
- Other → `~/.${shell}rc`

## Step 2: Explain What Setup Will Do

Before asking for any input, tell the user exactly what this skill will do:

```
AskUserQuestion:
  question: "Here's what setup will do. Ready to proceed?"
  header: "Council Setup"
  options:
    - label: "Let's go"
      description: "Proceed with setup"
      preview: |
        This setup will make 2 changes to your shell config ([config file]):

        1. ADD A SHELL ALIAS
           Creates an alias so you can launch Claude Code with the
           council plugin loaded from any directory.
           Example: alias council='claude --plugin-dir "/path/to/repo"'

        2. ENABLE AGENT TEAMS
           The council's evaluate skill uses Claude Code's teams feature
           to run parallel agent waves. This requires an env var:
           export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

        Both changes are tagged with "# public-goods-council" so they
        can be cleanly removed or updated by re-running setup.

        Nothing else is modified. No files outside your shell config are touched.
    - label: "Cancel"
      description: "Exit without changes"
```

If "Cancel" → report "Setup cancelled. No changes made."

## Step 3: Ask for Alias Name

```
AskUserQuestion:
  question: "Pick an alias name. You'll type this to launch Claude with the council loaded."
  header: "Alias Name"
  type: text
  placeholder: "e.g. council, pgc, eval"
```

Store as `$ALIAS_NAME`.

### Validate

- Non-empty
- Alphanumeric + hyphens + underscores: `[a-zA-Z0-9_-]+`
- No spaces

If invalid, explain and re-ask.

## Step 4: Validate Alias is Available

```bash
command -v $ALIAS_NAME 2>/dev/null; alias $ALIAS_NAME 2>/dev/null; echo "exit:$?"
```

If collision found:

```
AskUserQuestion:
  question: "'$ALIAS_NAME' already exists as [command/alias]. Use it anyway?"
  header: "Name Conflict"
  options:
    - label: "Use it anyway"
      description: "Overwrite the existing alias"
    - label: "Pick a different name"
      description: "Go back and choose another name"
```

If "Pick a different name" → loop back to Step 3.

## Step 5: Write to Shell Config

Build the lines to add. Two lines, both tagged:

For zsh/bash:
```
alias $ALIAS_NAME='claude --plugin-dir "$PLUGIN_DIR"'  # public-goods-council
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1  # public-goods-council
```

For fish:
```
alias $ALIAS_NAME "claude --plugin-dir '$PLUGIN_DIR'"  # public-goods-council
set -gx CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1  # public-goods-council
```

Before writing, remove any existing tagged lines:

```bash
grep -v '# public-goods-council' "$SHELL_CONFIG" > "$SHELL_CONFIG.tmp" && mv "$SHELL_CONFIG.tmp" "$SHELL_CONFIG"
```

Then append:

```bash
echo "" >> "$SHELL_CONFIG"
echo "$ALIAS_LINE  # public-goods-council" >> "$SHELL_CONFIG"
echo "$TEAMS_LINE  # public-goods-council" >> "$SHELL_CONFIG"
```

## Step 6: Report Success

```
Setup complete. Added to [config file]:

  [alias line]
  [teams env var line]

Activate now:
  source [config file]

Then launch from anywhere:
  $ALIAS_NAME

Inside a session, try:
  /council:evaluate Protocol Guild
  /council:design DeFi protocols
  /council:add-agent eval security

The alias points at your local clone — edit agents
or skills and changes are picked up immediately.
```
