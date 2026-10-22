# Auth (do not store secrets here)

Pi saves credentials in `auth.json` under the agent directory (`~/.pi/agent` unless `PI_CODING_AGENT_DIR` is set). That file is gitignored. Never commit it. Prefer environment variables in CI and on shared machines.

Machine login: `pi /login` (or `/login <provider>`), or set the provider's env var before starting Pi. `/logout` removes the stored credential; it does not unset env vars.

## Claude / Anthropic

Allowed:

- `ANTHROPIC_API_KEY` from Claude Console ([platform.claude.com](https://platform.claude.com)), billed to the key owner.
- Amazon Bedrock, Google Vertex AI, or Microsoft Foundry **when billed to the key owner**.

Not allowed:

- Claude Pro / Max / Enterprise **subscription** OAuth.
- `claude setup-token`.
- `ANTHROPIC_OAUTH_TOKEN` from claude.ai.
- Driving `pi-claude-agent-sdk` against a consumer or enterprise seat.

A Claude Enterprise seat does **not** include a model API key. claude.ai org API keys (`sk-ant-api01-...`) are admin / compliance / analytics keys, not the Messages API. Console is a separate product.

## Cursor

Cursor Desktop is not Pi's runtime. This config installs `pi-cursor-sdk` so Cursor appears in Pi's `/login` as an API-key provider.

Allowed:

- A **Cursor Dashboard API key** (user key, or a service-account key from Team settings).
- `CURSOR_API_KEY` in the environment.
- `/login` → Use an API key → Cursor. Pi stores it in `auth.json`.

Not allowed:

- Cursor Desktop login.
- Cursor Agent CLI / `agent status` subscription OAuth.
- Team Admin API keys (the Cursor SDK does not accept them).

After `/login`, run `/cursor-refresh-models` if the picker still shows only fallback models. Do not put the key in `cursor-sdk.json` or in this repo.

## GitHub

Two different GitHub credentials:

| Use | How |
| --- | --- |
| Model provider (Copilot) | `/login` GitHub Copilot, or `COPILOT_GITHUB_TOKEN` |
| Repo / PR / issue APIs | GitHub MCP or `gh` via bash |

GitHub MCP is **not** configured in `mcp.json` yet. A later option is `https://api.githubcopilot.com/mcp/` with a PAT, or calling `gh` from bash. Do not put tokens in this repo.
