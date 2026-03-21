Read this file, then follow the steps below to set up the council plugin for the user.

## Steps

1. Detect the user's shell (`$SHELL`) and resolve the config file:
   - zsh → `~/.zshrc`
   - bash → `~/.bashrc` (or `~/.bash_profile` on macOS if `.bashrc` doesn't exist)
   - fish → `~/.config/fish/config.fish`

2. Check if the council repo exists locally:
   - Look for `.claude-plugin/plugin.json` in the current directory
   - Check common locations: `~/git/octant-council-builder`, `~/octant-council-builder`, `~/projects/octant-council-builder`, `~/code/octant-council-builder`, `~/src/octant-council-builder`
   - If found, store the absolute path as `$PLUGIN_DIR`
   - If not found, set `$REPO_FOUND=false`

3. **Before doing anything else**, explain to the user what setup will do and ask for confirmation. Include:
   - How plugins work: `--plugin-dir` tells Claude Code to load `.claude-plugin/plugin.json` from a directory and register all `skills/*/SKILL.md` files as slash commands
   - If repo not found: that we'll clone it from `https://github.com/golemfoundation/octant-council-builder.git`
   - That we'll create a shell alias (e.g. `alias council='claude --plugin-dir /path/to/repo'`)
   - Why the alias is useful: keeps things isolated — the council only loads when you use the alias, plain `claude` stays clean
   - That we'll enable the agent teams env var (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
   - That the alias points at the local clone, so editing agent/skill markdown files takes effect immediately
   - Mention `/reload-plugins` for picking up skill changes during a live session
   - **Wait for user confirmation before proceeding. If they cancel, stop.**

4. If repo was not found, ask where to clone it (default: `~/git/octant-council-builder`) and run:
   ```bash
   git clone https://github.com/golemfoundation/octant-council-builder.git "$CLONE_DIR"
   ```
   Set `$PLUGIN_DIR` to the clone location.

5. Ask the user what alias name they want (e.g. `council`, `pgc`, `eval`, `betty`, `hal`).

6. Check the alias isn't already taken (`command -v` / `alias`). If it is, let them know and ask again.

7. Remove any existing lines tagged `# public-goods-council` from the config file, then append:

   For zsh/bash:
   ```bash
   alias NAME='claude --plugin-dir PLUGIN_DIR'  # public-goods-council
   export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1  # public-goods-council
   ```

   For fish:
   ```fish
   alias NAME "claude --plugin-dir PLUGIN_DIR"  # public-goods-council
   set -gx CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1  # public-goods-council
   ```

8. Tell the user to run:
   ```
   source [config file] && cd $PLUGIN_DIR && $ALIAS_NAME
   ```
   Then explain:
   - **How the alias works**: `--plugin-dir` loads the plugin from the repo. The council skills only appear when you use the alias — plain `claude` stays unaffected.
   - **Developing your council**: agents are markdown files in `agents/` — edit them and changes are picked up on the next `/council:evaluate`. Skills are in `skills/*/SKILL.md` — run `/reload-plugins` inside a session to pick up skill changes without restarting. No build step, no compilation.
   - **Sharing your council**: once you design your own council, push your fork and share the repo URL. Anyone can clone it and run `/council:settings` to install your council as a plugin.

=== OPTINPG EXTENSION START ===
/council:deploy-to-production [slug] – Exports the current council to a live
production web app on Railway (3 FastAPI/LangGraph services) + Netlify (Next.js 15
dashboard). Generates Ostrom radar charts, EAS attestation records, and shareable
project links. Safe to ignore for normal users.

/council:test-octant – Runs the full evaluation pipeline on 5 test Octant projects
(Protocol Guild, L2BEAT, growthepie, Revoke.cash, Tor Project) to verify all agents
work end-to-end. Output goes to council-out/.
=== OPTINPG EXTENSION END ===
