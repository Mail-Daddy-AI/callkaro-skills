# Reference: Capabilities & Pathway Nodes
<!-- graph-summary: Field reference for capabilities[] on multi-prompt (type 2) and pathway nodes (type 3): transitions, per-capability models/functions/post-call, the expression grammar for condition_type 1, and save-time normalisation. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 4. `capabilities[]` — type-2 capabilities and type-3 nodes

Shared fields (both types):

| Field | Type | Meaning |
| --- | --- | --- |
| `capability` | string, `snake_case`, unique | The identity key. Transitions target it by this exact string; renaming it is a graph-wide operation. Never translate it. |
| `is_starting` | bool | Entry point. **Exactly one** in the final set — save-time normalisation keeps the first `true` (or index 0) and clears the rest. |
| `system_prompt` | string | What the agent does and says **while this capability is active**. |
| `overwrite` | bool, `false` | `false` → the version `systemprompt` is **merged** with this prompt, so write only the phase-specific part. `true` → the base is **excluded** and this prompt must be fully self-contained (persona, tone, rules), or the agent changes character mid-call. |
| `msg_while_switching_type` | `silent` \| `static` \| `dynamic` | What the caller hears while switching **into** this capability. `silent` (default) = nothing; `static` = speak `msg_while_switching` verbatim; `dynamic` = `msg_while_switching` is a *prompt* for generating a bridging line. |
| `msg_while_switching` | string | The literal line, or the generation prompt. `""` for `silent`. |
| `endpointing` | `{mode, min_delay, max_delay}` | Controls when the caller's turn is complete while this capability/node is active. `mode` is `fixed` or `dynamic`; `min_delay` is 0–1 seconds and `max_delay` is 0–6 seconds. Defaults: `{ "mode": "fixed", "min_delay": 0.5, "max_delay": 3 }`. See below. |
| `llms` | `{primary_model, secondary_model, temperature}` | Per-capability model choice — how you control cost/quality per phase (cheap model for the greeting, stronger for negotiation). New-agent defaults are `callkaro/arjuna-2.5` / `gpt-5.4-nano` / `0.2`. **`temperature` here is 0–1** ([§7](llm-and-postcall.md)). |
| `functions` | object[] | Functions callable while inside this capability ([§6](functions-reference.md)). |
| `postcall` | object[] | Post-call variables scoped to this capability ([§8](llm-and-postcall.md)). |
| `use_filler` | bool | Use filler sounds during this capability. Only meaningful when version `filler_config.filler_type` ≠ `none`. |

Endpointing behavior:

- `min_delay` is the minimum silence after the caller stops speaking before the turn may end. Raising it reduces premature cutoffs but adds response latency.
- `max_delay` is the maximum silence the system may wait before ending the turn. Raising it allows longer thinking pauses but can make responses feel slower.
- `fixed` applies the configured timing consistently. `dynamic` adapts the wait to the caller's speech and conversation context while remaining between `min_delay` and `max_delay`.
- Treat `endpointing` as one complete nested object. When changing one member, preserve the current values of the other members and send the complete object.

Type-2 only:

| Field | Type | Meaning |
| --- | --- | --- |
| `stick_capability` | bool, `false` | `true` → once entered, this prompt stays appended for the rest of the call instead of being swapped out. Ignored on type 3 (persisted as `false`). |

Type-3 node-only fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `node_type` | `normal` \| `global` | `normal` = reachable only via an inbound transition. `global` = reachable from **anywhere**; the runtime tests `when_to_jump` every turn, jumps in, then **returns to the node it came from with context intact**. |
| `when_to_jump` | string | **Global nodes only** — natural-language trigger. Must be non-empty for `global` and empty for `normal`; both directions are validated. |
| `transitions` | object[] | Outgoing edges. Terminal nodes have `[]`; globals normally have `[]` because they return rather than route. |
| `extract_variables` | object[] | Values captured live inside this node. |
| `position` | `{x, y}` | Visual layout only, never semantic. |

Use `global` nodes for cross-cutting concerns: objection handling, "talk to a human", FAQ/knowledge
answers, opt-out/DND, abusive-caller handling. A global node is never "unreachable" for lacking an
inbound edge.

`transitions[]` entry:

| Field | Type | Meaning |
| --- | --- | --- |
| `condition_type` | `0` \| `1` | `0` = **prompt**: `condition` is natural-language intent judged by the model. `1` = **expression**: a deterministic boolean over variables. |
| `condition` | string | The intent text, or the expression. |
| `next_capability` | string | Exact name of an **existing** node. A dangling target fails validation. |

Prefer `condition_type: 1` whenever the branch depends on a value you already capture — it is
deterministic and debuggable. Use `0` only for genuinely intent-shaped branches no variable encodes.
Write the highest-priority edge first.

`extract_variables[]` entry:

| Field | Type | Meaning |
| --- | --- | --- |
| `type` | `string` \| `number` \| `boolean` | Only these three. |
| `name` | `snake_case` | What `condition_type: 1` expressions reference. |
| `description` | string | The complete spec for the extractor — be concrete. |
| `is_required` | bool | **A GATE.** `true` → the node takes **no** outgoing transition until this value is captured; the agent stays and keeps asking. `false` → optional, never blocks. |

`is_required: true` couples the prompt and the graph: write the gathering behaviour (re-ask,
rephrase, handle refusal) into `system_prompt`, and **never** mark a variable required if the caller
might legitimately refuse it — the gate blocks *every* outgoing edge including the "not interested"
escape, trapping the call. Prefer `true` for any variable an expression routes on, otherwise the
expression evaluates against a missing value. A variable is declared on the node that captures it
and stays readable by downstream nodes' expressions.

### Expression grammar (`condition_type: 1`) — strictly parsed

```
Comparison        := '(' operand comp_op operand ')'
LogicalExpression := '(' Expression (AND|OR) Expression [...] ')'
Expression        := Comparison | LogicalExpression
```

Every comparison gets its own parentheses; a joined expression gets **one more outer pair**, so a
logical operator never appears outside the outermost parens. Operators `== != >= <= > <`; logical
`AND` / `OR` **uppercase only**; booleans `True` / `False`; operands are an `extract_variables` name,
`metadata.some_var`, a number, or a `'quoted string'`.

| | |
| --- | --- |
| ✅ | `(escalation_needed==False)` |
| ✅ | `((escalation_needed==False) AND (complaint_resolved==True))` |
| ✅ | `((a==True) AND (b==False) AND (c==True))` |
| ✅ | `(((a==True) AND (b==False)) OR (c==True))` |
| ✅ | `((metadata.age > 18) AND (plan == 'pro'))` |
| ❌ | `(a==False) AND (b==True)` — no outer parens |
| ❌ | `age > 18` — no parens |
| ❌ | `((a==True) and (b==False))` — lowercase logic |

### Save-time normalisation of `capabilities[]`

Every capability is rewritten to exactly: `capability` (defaulting to `capability_<n>`),
`is_starting` (exactly one), `system_prompt` (`""`), `overwrite` (`false`), `stick_capability`
(`false`), `msg_while_switching_type` (`silent`), `msg_while_switching` (`""`), `llms` (defaults
filled), `functions` (`[]`), `postcall` (`[]`) — plus the four node fields when the capability looks
like a node (`node_type` `normal`, `transitions` `[]`, `extract_variables` `[]`, `when_to_jump` `""`).
Any per-capability `metadata` key is stripped. Don't rely on other ad-hoc keys surviving a save
through that path.
