# Reference: Versioning, Publishing & Pre-flight Checklist
<!-- graph-summary: How versions, commits, publishing, A/B routing and cloning work at field level, plus the pre-flight checklist to run before publishing. -->

Part of the [version reference](../AGENT-VERSION-REFERENCE.md) (which document a field belongs to, topic map). Field index: [field-index.md](field-index.md).

## 16. Versioning & publishing

Versions are append-only in practice: prefer creating a **new version** over editing a published one.
Every write also records a commit snapshot, so version history is queryable and comparable.

| Concern | Field / endpoint |
| --- | --- |
| Version label | `versionName` (version doc) |
| Enable / disable a version | `isVersionActive` (bool, default `true`) · `PUT /v2agent/toggleVersionActive/:id` |
| Publish for a language | `publishedVersionsByLanguage` — one entry per version `default_language`; publishing **replaces** the existing entry for that language · `PUT /v2agent/publishAgent/:id` |
| Version shown in the UI | `publishedVersionId` + `lastPublishedDate` |
| Live / not live | `agentStatus`: `live` \| `in-progress` |
| New agent (agent + first version in one body) | `POST /v2agent` — body split per [§1](../AGENT-VERSION-REFERENCE.md); the first version auto-publishes for its language |
| New version on an existing agent | `POST /v2agent/createNewVersion/:id` — body `versionName` + version fields |
| Edit a version | `PUT /v2agent/:id?version=<versionId>` — **the `version` query param is required** for any version field, otherwise the request is rejected (400) |
| Read | `GET /v2agent/:id?version=<versionId>` — returns agent+version merged, plus all versions |
| Duplicate | `PUT /v2agent/duplicate/:id` |
| Export / import versions | `POST /v2agent/:id/export` (`{versionIds}`) · `POST /v2agent/:id/import-versions` (array of version payloads) |
| Delete a version | `DELETE /v2agent/deleteversion/:id` |
| Compare versions | `POST /v2agent/compareVersions` |

Behaviours to rely on:

- A brand-new version auto-publishes **only if** no version is published yet for its
  `default_language`; it never steals an existing published slot.
- On `PUT /:id`, plain objects are **merged key-by-key**, *except* `preFormatVariables`,
  `customPronunciations`, `transcriber`, `secondary_transcriber`, `voice_configuration`,
  `secondary_voice_configuration`, `callFlow_json`, `variableSource`, which are **replaced
  wholesale**. To remove one key from a merged object, send the whole object without it.
- Optimistic conflict detection: send `originalSystemPrompt`, `originalRole`, `originalGoal`,
  `originalCallFlow`, `originalModelResponseSnippet`, `originalSecurityGuardrailsSnippet` alongside
  your edit and you get a `409` with a line-level `conflicts[]` list if the server copy moved
  underneath you. Pass `commitMessage` to label the commit.
- Export strips ids, ownership, phone numbers, knowledge bases and switchable entities and adds an
  encrypted source-agent marker; WhatsApp-type functions are stripped when importing across accounts.

---

## 19. Pre-flight checklist

Structural — a violation throws, or silently corrupts the agent:

- [ ] Every key is on the **right document** ([§1](../AGENT-VERSION-REFERENCE.md)) and declared ([§18](../AGENT-VERSION-REFERENCE.md)).
- [ ] Type-appropriate script fields populated; the other types' fields emptied.
- [ ] Types 2/3: exactly **one** `is_starting`; capability names unique and `snake_case`.
- [ ] Type 3: every `next_capability` exists; every `global` node has a non-empty `when_to_jump`; no
      `normal` node has one; every `condition_type: 1` expression is fully parenthesised with
      uppercase `AND`/`OR`; every expression variable is declared in some node's `extract_variables`
      (apart from `metadata.*`); no unreachable node; terminal nodes exist and are reachable.
- [ ] Voice/transcriber values copied verbatim from the resolved catalogue; only provider-valid keys
      present; `transcriber_language` in that provider's own format (array for
      Azure/Soniox/Callkaro).
- [ ] Realtime LLM ⇒ Open AI voice; non-realtime LLM ⇒ not Open AI.
- [ ] Function names unique within scope; parameters only `string`/`number`; no `PATCH`; post-call
      `parameters` is a JSON **string**; warm transfers have a non-empty prompt; every WhatsApp
      template placeholder mapped.
- [ ] `temperature` on the right scale — version 0–10, capability `llms` 0–1.
- [ ] `version` query param present when editing version fields.

Quality — nothing validates these, and they are what make the agent good:

- [ ] No routing prose inside a type-3 `system_prompt`.
- [ ] Every `is_required: true` variable has matching gathering instructions, and no required
      variable can trap a caller who legitimately refuses.
- [ ] `end_call_msg` contains only genuine final lines.
- [ ] One persona gender across the base prompt, every capability, every snippet, and the voice.
- [ ] Operational text in English; only spoken lines in the target language.
- [ ] No `extract_variable` duplicated as a post-call variable on the same node.
- [ ] `overwrite: true` prompts are genuinely self-contained.
- [ ] Every `{{metadata}}` reference has a fallback, so no empty placeholder is ever spoken.
- [ ] Post-call variable descriptions are precise enough to serve as an extraction spec.
