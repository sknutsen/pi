# Pi user config

Git-backed source of truth for this operator's [Pi](https://pi.dev) (`@earendil-works/pi-coding-agent`) **user** directory. Cursor (personal) and Claude Code (work) stay on agent-kit. Pi is a third host. Skills stay in agent-kit; this repo does not fork them.

The live agent directory is `~/.pi/agent` unless `PI_CODING_AGENT_DIR` is set. After install, that directory is a set of links into this tree, not an untracked snowflake.

Default UI is the TUI (`@earendil-works/pi-tui`). Extensions, `pi --mode rpc`, and the SDK can drive other UIs later. This repo does not install `pi-rpc-web`, `pi-web-ui`, or `pi-code`. `pi-cursor-sdk` is declared in `settings.json` so `/login` can use a Cursor Dashboard API key.

## Layout

```text
README.md
.gitignore
flake.nix                   # Pi CLI + nix run .#install
scripts/install.py          # python3; --status and --uninstall
settings.json
keybindings.json            # empty besides $schema; /hotkeys shows defaults
mcp.json                    # no servers yet (no secrets)
models.json                 # empty providers stub; no API keys
APPEND_SYSTEM.md            # appended to Pi's system prompt
AGENTS.md                   # short always-on user context
extensions/                 # drop a .ts file here; see extensions/README.md
prompts/                    # slash-command templates later
themes/                     # custom themes later; default theme is "system"
docs/auth.md                # how to log in; what not to do
```

Not in git, never created by the installer: `auth.json`, session dumps, a `skills/` copy, `SYSTEM.md` (that would replace Pi's default prompt).

## Clone and install

Nix hosts (Apple Silicon macOS, Linux, WSL). Clone first — the installer links `~/.pi/agent` to this checkout, not the Nix store:

```bash
git clone <this-repo> ~/Code/pi   # Linux/WSL: ~/code/pi
cd ~/Code/pi                      # Linux/WSL: cd ~/code/pi
nix run .#install
nix run .#status
nix profile add .                 # Pi CLI from github:earendil-works/pi/stable
```

`nix develop` (or direnv) puts `pi` and `python3` on PATH. Update Pi with `nix flake update pi` then `nix profile upgrade pi`. `pi update` cannot update a Nix install.

Home Manager (from `~/.nixconf` or similar):

```nix
# flake input: pi-config.url = "github:sknutsen/pi";
imports = [ inputs.pi-config.homeModules.default ];
programs.pi-user-config.enable = true;
```

Activation clones `https://github.com/sknutsen/pi.git` into `~/Code/pi` (Linux/WSL: `~/code/pi`) when that path is missing. It does not pull an existing checkout.

Without Nix:

```bash
# macOS: ~/Code/pi   Linux/WSL: ~/code/pi
git clone <this-repo> ~/Code/pi
cd ~/Code/pi
python3 scripts/install.py
python3 scripts/install.py --status
```

```powershell
# Native Windows (PowerShell). Developer Mode helps file symlinks; directories use junctions.
py -3 scripts\install.py
py -3 scripts\install.py --status
```

The installer creates `~/.pi/agent` if needed and links only the files this repo manages. It refuses to replace foreign files and never writes, overwrites, or deletes `auth.json`.

Then **restart Pi**, or in an existing session run `/reload`.

## Run Pi

On Nix, `nix profile add .` (or `nix develop`) provides `pi`. Otherwise install the binary separately:

```bash
curl -fsSL https://pi.dev/install.sh | sh
# or: npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

Then start it in a project directory (TUI is the UI for now):

```bash
cd /path/to/a/project
pi
```

Windows: `powershell -c "irm https://pi.dev/install.ps1 | iex"`. Authenticate with `/login` or env vars; see [docs/auth.md](docs/auth.md).

## Auth

See [docs/auth.md](docs/auth.md). Short version: `pi /login` or env vars; never commit `auth.json`. Claude Console API keys are allowed; Claude Pro/Max/Enterprise subscription OAuth is not. Cursor login is a Dashboard API key via `pi-cursor-sdk`, not Desktop OAuth.

## Skills

Pi discovers Agent Skills from `~/.agents/skills`. agent-kit's `scripts/install.py` already links skills there (`agents_compat`). Reuse that. Do not copy skill trees into this repo. `settings.json` does not point `skills` at a local copy.

## Keybindings

`keybindings.json` is an empty schema stub on purpose. Run `/hotkeys` in Pi to see defaults. Put overrides in `keybindings.json` only when you actually want them. Do not invent custom shortcuts in this repo unless you need them.

## MCP

`mcp.json` is `{ "mcpServers": {} }`. GitHub MCP (`https://api.githubcopilot.com/mcp/` with a PAT, or `gh` via bash) is a later option. Do not add servers that need secrets until those secrets live outside git.

## Out of scope

- Kubernetes, Helm, Docker-in-cluster, cluster YAML
- Web UI / RPC clients (`pi-rpc-web`, `pi-web-ui`)
- `pi-code`
- A Pi source fork
- Employer secrets, internal URLs, job-only runbooks
