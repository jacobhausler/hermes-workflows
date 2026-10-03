# Proposed core hook: tool-result card rendering (optional, upstream-shaped)

> **Status: PROPOSAL ONLY — the plugin does not patch core and never will by
> itself.** Stock Hermes is unaffected: the plugin works as today, with the
> `::workflow{id="..."}` paste path plus the run payload's `card` / `hint` /
> `lifecycle_notice` fields. If upstream adopts the hook below, the desktop
> card additionally renders from the tool-result record and a model that
> forgets the paste still surfaces the card. This is the belt BEHIND the
> belt; the paste path stays (belt AND suspenders).

## Why (issue #157)

Card emission is model-honored, not enforced: a model that forgets to paste
the `::workflow{id="<run_id>"}` line produces a perfectly running, invisible
workflow. The plugin cannot close this plugin-side. Probed facts from the
packaged desktop SDK (`apps/desktop/src/sdk/index.ts` and its renderer):

* The transcript exposes exactly ONE plugin surface — the directive area:

  ```ts
  // sdk/index.ts
  export {
    TRANSCRIPT_DIRECTIVE_AREA,
    type TranscriptDirectiveContribution,
    type TranscriptDirectiveProps
  } from '@/lib/transcript-directives'
  ```

  and `TranscriptDirectiveContribution` is model-text-addressed only
  (`name` + `render({attrs, source, streaming})`). No tool call/result in props.

* Tool results render through `components/assistant-ui/tool/fallback.tsx`,
  whose per-tool special cases are core-internal string comparisons
  (`part.toolName === 'terminal'`, `'web_search'`, `'memory'`, …). No
  contribution registry, no slot a plugin can claim.

* `host.onEvent` hears the gateway stream (transient events), but there is no
  API to attach a component to a settled tool-call part.

So the missing primitive is a **tool-result contribution slot** — keyed by
(tool name, result shape), renderer-side, registry-backed like every other
area.

## The patch (≈30 lines, additive)

### 1. New area + payload type — `lib/tool-result-contribs.ts` (new file)

```ts
import type { ReactNode } from 'react'

/** TRANSCRIPT TOOL-RESULT contributions: a plugin claims tool calls by
 *  (toolName, result-shape) and its component renders under the tool chip.
 *  The gate is the plugin's own `claim` over the settled result — nothing
 *  renders unless a plugin claims the record. */
export const TOOL_RESULT_AREA = 'transcript.toolResults'

export interface ToolResultContribution {
  /** Claim a settled tool-result record for this tool name. Pure. */
  claim: (record: { toolName: string; args: unknown; result: unknown }) => boolean
  render: (record: { toolName: string; args: unknown; result: unknown }) => ReactNode
}

export interface ToolResultProps {
  toolName: string
  args: unknown
  result: unknown
}
```

### 2. Export from the SDK — `sdk/index.ts`

```ts
export {
  TOOL_RESULT_AREA,
  type ToolResultContribution,
  type ToolResultProps
} from '@/lib/tool-result-contribs'
```

### 3. One resolution point — `components/assistant-ui/tool/fallback.tsx`

Inside the tool-part renderer, beside the existing `part.toolName === …`
special cases, consult the registry (the same `useContributions` pattern the
directive leaf uses):

```tsx
const claims = useContributions(TOOL_RESULT_AREA).filter(c =>
  (c.data as ToolResultContribution).claim({ toolName: part.toolName, args: part.args, result: part.result }))
// …below the tool chrome:
{claims.map(c => (
  <ContribBoundary key={c.id} id={c.id} variant="chip">
    {(c.data as ToolResultContribution).render({ toolName: part.toolName, args: part.args, result: part.result })}
  </ContribBoundary>
))}
```

First claim wins per (area, toolName) if upstream prefers exclusivity; the
`ContribBoundary` isolation matches the directive leaf so a throwing plugin
degrades to an inline error, never a dead message.

## What the plugin would then register (one block, `desktop/plugin.js`)

```js
ctx.register({
  id: 'tool-result-card',
  area: TOOL_RESULT_AREA,
  data: {
    // keyed on toolset + action + result shape: only our run-launch payload
    claim: r => r.toolName === 'workflow' && r.args?.action === 'run' &&
                typeof r.result?.run_id === 'string' && typeof r.result?.card === 'string',
    render: r => jsx(DirectiveCard, { id: String(r.result.run_id) })
  }
})
```

Gated in the render on `run.json owner.session_id == viewing session` exactly
as `SessionStrip` already pairs `host.state.focusedSessionId` /
`focusedStoredSessionId`, so a card only mounts in the owning chat.

## Plugin-side readiness

The door already returns `{run_id, models, routes, hint, card,
lifecycle_notice}` on `action=run` (and `lifecycle_notice` on lane-key
dedupe), so the result-shape key above (`result.run_id && result.card`) is
stable contract, pinned by `tests/test_card_notice_157.py` and
`tests/test_card_backend_080.py`. If upstream lands the hook, the plugin adds
only the registration block plus a pure matcher pin; nothing here needs to
change first, and the paste path is never removed.
