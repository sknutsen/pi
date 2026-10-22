# Operator notes

This operator also uses Cursor (personal) and Claude Code (work). Pi is a third host.

Shared workflows live in agent-kit skills and are discoverable via `~/.agents/skills`. Prefer those over inventing parallel procedures.

Git: never commit, push, amend, or force-push unless the user explicitly asked. Never skip hooks. Follow the git-commit / create-pull-request skills when those apply.

Do not put employer secrets, internal URLs, or job-only runbooks in this config repo or in agent-kit.

Safety gap: Pi does not yet run agent-kit's `hooks/policy.json`. Be extra careful with `rm`, private keys, `.env`, and writes outside the working tree. A Pi extension wrapping that policy is future work.

UI: default is the TUI. Custom TUI widgets belong in `extensions/`. A web UI would be an RPC client later, not a fork.
