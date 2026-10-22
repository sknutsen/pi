# Pi extensions

Drop a TypeScript (or JavaScript) module in this directory. Pi auto-loads files here and subdirectories that contain `index.ts` or `index.js`. If a copy lives somewhere else, add that path to `settings.json` `extensions`.

Reload with `/reload` after adding or editing an extension.

## UI vs print/RPC

`ctx.ui` is the interactive UI. Guard terminal-only work so print and RPC still work:

- `ctx.mode === "tui"` — real TUI (`@earendil-works/pi-tui`). Use this for `ctx.ui.custom()` and other terminal-only widgets.
- `ctx.hasUI` — dialogs and notifications that interactive *and* RPC clients can handle (`select`, `confirm`, `notify`, …). False in JSON/print mode.

Keep tool and event behavior independent of rendering.

## Later goals (not in this repo yet)

- A permission gate around agent-kit `hooks/policy.json` / `policy.py` (Pi does not run those hooks today).
- Persistent TUI widgets.
- Extra model providers.

Do not load untrusted extensions. They run inside the Pi process.

`example.template.ts` is an inert commented scaffold. Copy it to a `.ts` file to load it; the `.template.ts` suffix is not auto-loaded.
