// Inert scaffold. Copy to a .ts file in this directory to load.
// Named *.template.ts so Pi does not auto-load it.
// No network, no secrets, no tools.

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (_pi: ExtensionAPI) {
  // Register tools, commands, or UI from here.
  // Guard TUI-only widgets with ctx.mode === "tui".
  // Guard dialogs with ctx.hasUI so print/RPC still work.
}
