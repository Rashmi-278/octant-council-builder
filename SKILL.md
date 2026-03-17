Read this file, then follow the steps below to set up the council plugin for the user.

## Steps

1. Detect the user's shell (`$SHELL`) and resolve the config file:
   - zsh → `~/.zshrc`
   - bash → `~/.bashrc` (or `~/.bash_profile` on macOS if `.bashrc` doesn't exist)
   - fish → `~/.config/fish/config.fish`

2. Resolve the absolute path to this repo:
   ```bash
   PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
   ```
   (or equivalent — the directory containing this file)

3. Ask the user what alias name they want (e.g. `council`, `pgc`, `eval`).

4. Check the alias isn't already taken (`command -v` / `alias`). If it is, let them know and ask again.

5. Remove any existing lines tagged `# public-goods-council` from the config file, then append:

   For zsh/bash:
   ```bash
   alias NAME='claude --plugin-dir "PLUGIN_DIR"'  # public-goods-council
   export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1  # public-goods-council
   ```

   For fish:
   ```fish
   alias NAME "claude --plugin-dir 'PLUGIN_DIR'"  # public-goods-council
   set -gx CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1  # public-goods-council
   ```

6. Tell the user to run `source CONFIG_FILE`, then they can launch from anywhere with their alias.
