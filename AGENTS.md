# AGENTS.md

Personal user-level context for Pi. This does not replace Pi's default system prompt; operator notes that append to that prompt live in `APPEND_SYSTEM.md`.

This operator keeps **agent-kit** as portable identity: skills, agents, and a safety policy. Cursor is the usual host for personal work. Claude Code is the usual host for work. Pi is a third host. Skills stay in agent-kit; this repo is Pi *user* config only.

Shared workflows are discovered through Pi's native Agent Skills path, `~/.agents/skills` (agent-kit's installer links them there). Prefer those skills over inventing parallel procedures. Do not copy skill trees into this repo.

Pi does not yet evaluate agent-kit's `hooks/policy.json`. Treat `rm`, private keys, `.env`, and writes outside the working tree with extra care.
