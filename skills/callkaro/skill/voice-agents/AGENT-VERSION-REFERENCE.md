# CallKaro Agents & Versions — Complete Reference
<!-- graph-summary: Router for the agent and version field reference: which document (agent or version) a key belongs to, UI-only fields, and which topic node to open (script, capabilities, functions, LLM and post-call, voice, call settings, variables and memory, versioning, payloads, field index). Read first, then open only the node you need. -->

**Read this first for anything with agents or versions.** It tells you which document a
field lives on and which topic node defines it, with its allowed values and the traps
that silently drop data. Open only the node the task needs.

---

---

## Which node to open

Open only what the task needs. Each node keeps its original section numbers.

| Task | Node |
| --- | --- |
| Prompt type, script fields, snippets, variable namespaces, how a call runs ([§2](reference/script-and-types.md), [§3](reference/script-and-types.md), [§5](reference/script-and-types.md)) | [script-and-types.md](reference/script-and-types.md) |
| Multi-prompt capabilities or pathway nodes, transitions, expression grammar ([§4](reference/capabilities-and-pathways.md)) | [capabilities-and-pathways.md](reference/capabilities-and-pathways.md) |
| Adding or changing functions: types, field sets, predefined, conditions ([§6](reference/functions-reference.md)) | [functions-reference.md](reference/functions-reference.md) |
| Advanced pre-call protocols, email helpers ([§6](reference/functions-reference.md)) | [functions-advanced-code.md](reference/functions-advanced-code.md) |
| Models, temperature, caching, post-call analysis ([§7](reference/llm-and-postcall.md), [§8](reference/llm-and-postcall.md)) | [llm-and-postcall.md](reference/llm-and-postcall.md) |
| Voice and transcriber keys per provider ([§9](reference/voice-and-transcriber-fields.md), [§10](reference/voice-and-transcriber-fields.md)) | [voice-and-transcriber-fields.md](reference/voice-and-transcriber-fields.md) |
| Opening/ending a call, silence, language switching, VAD, noise, voicemail, DTMF, webhook ([§11](reference/call-settings.md)-[§13](reference/call-settings.md)) | [call-settings.md](reference/call-settings.md) |
| Variables and formatting, knowledge, filler, pronunciation, call memory, voice rotation, WhatsApp ([§14](reference/variables-memory-whatsapp.md), [§14b](reference/variables-memory-whatsapp.md), [§15](reference/variables-memory-whatsapp.md)) | [variables-memory-whatsapp.md](reference/variables-memory-whatsapp.md) |
| Versions, publishing, A/B, cloning, pre-flight checklist ([§16](reference/versioning-and-preflight.md), [§19](reference/versioning-and-preflight.md)) | [versioning-and-preflight.md](reference/versioning-and-preflight.md) |
| Copy-paste create/update payloads ([§20](reference/minimal-payloads.md)) | [minimal-payloads.md](reference/minimal-payloads.md) |
| Which node holds field X ([§17](reference/field-index.md)) | [field-index.md](reference/field-index.md) |

---

## 1. Field routing — agent doc vs version doc

The API splits one flat request body by an allow-list. Exactly these keys go to the **agent**
document; **every other key** goes to the version document:

```
folderId · name · systempromptType · phoneNumber · inboundPhoneNumbers ·
outboundPhoneNumber · secondaryOutboundPhoneNumber · whatsappPhoneNumber ·
whatsappInboundPhoneNumber · publishedVersionId · lastpublisedDate ·
abTestVersions · abTestEnabled · advancedAbTestEnabled · advancedAbTestRules ·
advancedAbTestMode · advancedAbTestJsCode ·
_id · default_agent_language ·
useMultiTranscribers · publishedVersionsByLanguage · agentStatus
```

(`lastpublisedDate` is spelled exactly like that in the allow-list; the stored field is
`lastPublishedDate`.)

### Agent-document fields

| Field | Type | Meaning |
| --- | --- | --- |
| `name` | string, **required** | Display name, e.g. `"Riya – Sales Outreach"`. |
| `folderId` | ObjectId \| null | Folder, for organisation only. |
| `default_agent_language` | `en hi kn ta te mr gu bn ml` | The agent's primary language. The per-version `default_language` is what actually drives a call. |
| `outboundPhoneNumber` | ObjectId | Number used to place outbound calls. |
| `secondaryOutboundPhoneNumber` | ObjectId | Fallback outbound number. |
| `inboundPhoneNumbers` | ObjectId[] | Numbers whose inbound calls route to this agent. |
| `phoneNumber` | string[] | Legacy plain-string numbers. |
| `whatsappPhoneNumber` / `whatsappInboundPhoneNumber` | string | WhatsApp routing. Assigning an inbound WhatsApp number detaches it from any other agent holding it. |
| `publishedVersionsByLanguage` | `[{versionId, lastPublishedDate}]` | **The live version per language.** At most one entry per version `default_language`. |
| `publishedVersionId` | ObjectId | The version the app UI opens by default. |
| `lastPublishedDate` | Date | Set alongside `publishedVersionId`. |
| `agentStatus` | `live` \| `in-progress` | `in-progress` = still being built. |
| `abTestEnabled` / `abTestVersions` | bool / `[{versionId, ratio 0–100}]` | Traffic split across versions. **Never modify as a side effect** of another change. |
| `advancedAbTestEnabled` / `advancedAbTestRules` | bool / rule array | **Rule-based A/B**: ordered if/elseif/else chain over call `metadata.*`, evaluated BEFORE the ratio A/B (only when no version is pinned). Each rule: `{kind: if\|elseif\|else, condition, returnType: version\|language, targets:[{versionId\|language, ratio}]}`. `version` short-circuits (that version runs); `language` only overrides language and resolution continues. Conditions use the [§4](reference/capabilities-and-pathways.md) expression grammar with `metadata.*` operands; ratios are integers summing to 100 per rule. Manage via `ck agents ab-advanced`. |
| `advancedAbTestMode` / `advancedAbTestJsCode` | `rules` \| `js` / string | **JavaScript routing** instead of the rule chain: `async function route(context)` with `context = {metadata, versions, languages}` returns a version id, a language, or nothing (ratio A/B decides). Errors, invalid returns and runs over 5 s fall back to the ratio A/B. Default mode `rules`. Manage via `ck agents ab-advanced --js / --test / --mode` (MCP `test_ab_routing_js`); see [versions.md](versions.md). |
| `useMultiTranscribers` | bool | Run the primary and secondary transcriber simultaneously instead of primary-with-fallback. |
| `systempromptType` | int 0–3 | Routed here, but **not stored** — see the trap below. |

### ⚠️ The `systempromptType` trap

`systempromptType` sits in the agent allow-list, but the agent document does not declare it — so a
value sent through `POST /v2agent`, `PUT /v2agent/:id`, `createNewVersion` or `importVersions` is
routed to the agent doc and then dropped, leaving the **version** at its default `0`.

Consequences:

1. Through those endpoints, express the type **structurally** ([§2](reference/script-and-types.md)) rather than relying on the field.
2. When the stored value is absent the type is *inferred*: non-empty `capabilities[]` → **2**, or
   **3** if any capability carries `node_type` / `transitions` / `extract_variables` /
   `when_to_jump`; else non-empty `role` / `goal` / `callFlow` → **1**; else **0**.
3. Writers that create versions through the internal service layer *do* set it explicitly, and it is
   authoritative when present. If your path can set it, set it — and keep it consistent with the
   structure, because a mismatch (`systempromptType: 2` with no capabilities) yields an agent that
   behaves like neither type.

---

## 18. UI-exposed fields the version document may not persist

These appear in the web builder but are **not declared on the version document** in the deployment
this reference was written against, which means a plain write is silently discarded:

`dtmf_collection_enabled` · `callPropertyMapping`

Before promising any of them to a user: write the value, read the version back, and confirm it
round-tripped. If it didn't, say so plainly instead of reporting success — the write returns 200
either way. (Nested keys inside free-form objects are unaffected and persist normally, including
`use_filler` and `to_numbers` inside `capabilities[]`/`functions[]` and every provider-specific
voice/transcriber key.)

Also treat as read-only unless explicitly asked: `vad_configuration` (system-tuned),
`abTestEnabled` / `abTestVersions` (traffic splitting), `position` on pathway nodes (layout).
