<!-- graph-summary: The ck CLI: rules that bite on every write (whole objects, whole function arrays, changed fields only), raw call logs, export/import, and what ck cannot do. Use for terminal work. -->
<!-- source: callkaro-skills command docs, plus the CLI guidance in TejasLamba2006/callkaro-skills skills/callkaro-cli @ 1171578, reduced to commands ck documents -->
<!-- audience: ck -->

# The ck CLI

`ck` is the official CallKaro CLI (`npm install --global @callkaro-official/cli`). It is the default
for every command in this skill. Sign-in and account state: [auth.md](../auth.md). Each entity node
(agents, calls, numbers, batches, simulations, workflows, contacts, secrets) lists its own commands;
this node holds what applies to all of them.

## Before anything else

```bash
ck whoami --json     # logged in, as whom, credits
ck config            # endpoints and the account in use
```

- **Never invent ids.** Every id comes from a `list` or `get` first. Ids are 24-character hex strings.
- **Use `--json` when you will parse the output.** Human tables are not a stable interface.
- **Prefer the file form for JSON** (`--file agent.json`, `--set @patch.json`): it is quote-proof in
  every shell.

## Writes: the rules that bite

1. **Version-level fields need `--versions <versionId>`.** Without it the update is refused.
2. **Objects are replaced, not merged.** The backend replaces `voice_configuration`, `transcriber`,
   `secondary_*`, `preFormatVariables`, `customPronunciations`, `callFlow_json` and `variableSource`
   wholesale. `ck` sends what you give it, so a partial object erases every key you left out (an
   agent with no voice). Read the current value, edit it, send the whole object back.
3. **`functions` is replaced as a whole array.** Sending one function deletes every other function on
   that version, and the response still says the update succeeded. Always send the complete array.
4. **Send only the fields you are changing.** The update validates every field it is sent, so an
   untouched field from a full read-back can be rejected (an empty `capabilities` list on a basic
   prompt is refused).
5. **Database-managed fields are rejected**: `_id`, `__v`, `createdAt`, `updatedAt`, `userId`,
   `agentId`. `ck agents get --json` output contains them, so never feed it straight back in.
6. **Read back after every write** (`ck agents get <id> --versions <vid> --json`). A success message is
   not proof; some fields drop silently ([AGENT-VERSION-REFERENCE.md](../agents/AGENT-VERSION-REFERENCE.md) §18).

## Version lifecycle

```bash
ck agents clone-version <id> --versions <src> --name v2 --prompt-type 1 --language hi
ck agents update <id> --set @patch.json --versions <new>
ck agents publish <id> --versions <versionId>        # only when asked
ck agents toggle-active <id> --versions <versionId>
```

Write a change as a new version; never edit a live version in place. Details:
[versions.md](../agents/versions.md).

## Reading a call's raw log

```bash
ck calls logs <callId>
ck calls logs <callId> "grep -iE 'error|warning' /call.log"
```

The fastest way to diagnose a failed call: start here before theorising. Method:
[review-debug](../quality/review-debug.md).

## Export and import

```bash
ck agents export <id> --versions <v> --file a.json
ck agents import a.json
```

Export output often fails import: the export leaves out fields import requires (commonly
`language_switching_instructions`, `silence_instructions`, `language_lockin_time`,
`allowed_languages`, `language_switch_min_words`). Add each field it names, taking the real value
from `ck agents get <id> --versions <v> --json`.

## Simulations

`ck sim create`, `ck sim run`, `ck sim runs`, `ck sim results`, `ck sim tests`, `ck sim delete`:
[simulations.md](../simulations.md). Runs are asynchronous: poll `ck sim results`. To measure how
often a failure happens, run the same case several times.

## Not available in ck

These need the dashboard (or the internal API); there is no `ck` command, so do not invent one:

- the model lists per slot (agent, post-call, simulation caller)
- KPI Manager and its pending-task board ([kpi-manager](../platform/kpi-manager.md))
- chat-agent simulations and chat audits
- scheduled-call queues
- talking to an agent in text without a call
- switching between several saved accounts or client accounts

Never use internal admin or impersonation routes to reach another account's data.
