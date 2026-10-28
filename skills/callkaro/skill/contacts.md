<!-- graph-summary: CRM contacts: attribute schema, create, upload, update, delete, assign to an agent or workflow. Use when managing leads or the fields a workflow or agent reads. -->
# Contacts (CRM)

A contact is a **phone number plus attributes**. Attributes are fields the
account **defines first** (name, type, optional allowed values); contacts can
only hold attributes that have a definition. Workflows read and write these
same attributes — see [workflows-and-contacts.md](workflows-and-contacts.md).

## Ground rules

1. **Define an attribute before using it.** `upload` and `update` refuse a name
   with no definition (naming the offenders) instead of dropping data silently.
2. **Use phone numbers as digits with country code** (`919812345678`, no `+` or
   spaces) — imports and attribute updates strip non-digits, so this is the form
   every other command will match.
3. **Assigning contacts places real calls or sends real messages** — see
   [Assign](#assign). Confirm with the user first; test on one number.
4. **Destructive:** `delete`, `attributes delete`. They confirm unless `--yes` — don't pass `--yes` without the user's say-so.

## Commands

| Command | What it does |
|---|---|
| `ck contacts list [filters] [--page n] [--page-size ≤50] [--columns a,b] [--json]` | Browse. Filters: `--search`, `--channel`, `--attr name=value` (repeatable), `--last-message-state read\|delivered\|sent\|failed\|clicked\|not_clicked`, `--created-from/--created-to/--updated-from/--updated-to YYYY-MM-DD` (IST), `--assigned-to-me` |
| `ck contacts get <phone> [--json]` | One contact with its attributes |
| `ck contacts create <phone> [--attr name=value …] [--channel c …]` | Create, or merge into an existing contact |
| `ck contacts update <phone> [--attr name=value …] [--clear name …]` | Set or clear attributes (validated against the definitions) |
| `ck contacts delete <phone> [--yes]` | Delete |
| `ck contacts upload <file.csv> [--ignore-unknown]` | Bulk import |
| `ck contacts export [filters] [--fields a,b] [--file out.csv] [--email you@x.com]` | Export. Over 5000 rows it is **emailed** (`--email` required) |
| `ck contacts assign …` | Put contacts into a workflow or a voice-agent call run — see below |
| `ck contacts attributes list [--json]` | The definitions: name, type, enum options, flags |
| `ck contacts attributes set <name> [--type …] [--label] [--description] [--options a,b] [--manual-only\|--ai-updatable] [--required\|--optional] [--hidden\|--visible] [--default-mode drop\|type_default\|custom] [--default-value v]` | Create, or change **only the flags you pass** on an existing attribute |
| `ck contacts attributes delete <name> [--yes]` | Soft delete: values on contacts are kept but hidden |

Attribute types: `string description enum number date boolean datetime time array object`.
`enum` needs `--options`. `--manual-only` stops AI/functions overwriting it.

## Attributes

```bash
ck contacts attributes list --json
ck contacts attributes set city --type string --label "City"
ck contacts attributes set stage --type enum --options new,contacted,qualified,lost
ck contacts attributes set stage --options new,contacted,qualified,won,lost   # edits only options
```

`--attr name=value` values are strings on the command line; the server coerces
them by the attribute's type (`true/yes/1` for boolean, ISO or common formats
for dates). A value that doesn't fit is **refused with the reason**, not
guessed. An empty value (or `--clear name`) removes it.

### Hand-set values are protected from workflows

A value set by a person — `ck contacts update`, `ck contacts create --attr`, or an
edit in the dashboard — is marked **manual**, and **automated writes will not
overwrite it**: a workflow's Update Contact node, an agent's post-call update, and
CSV re-imports all skip an attribute whose current value was set by hand (verified:
a workflow marked a CSV-imported contact `won` but left a hand-edited one at
`contacted`). Only another manual edit changes it. So don't pre-set, by hand, an
attribute a workflow is meant to update; and if one "didn't update", check how its
value was last set (`ck contacts get <phone> --json` → the attribute's `source`).

## Import (CSV)

```csv
phone_number,name,city,stage
919812345678,Jatin,Delhi,new
919811111111,Asha,Mumbai,contacted
```

- Header row required, and the phone column must be named **`phone_number`**
  (unlike `ck batches`, where it is simply column 1).
- Every other column must match a defined attribute (case-insensitive). Unknown
  columns **refuse the whole file**, listing them — define them first, or pass
  `--ignore-unknown` to drop those columns.
- Cells are type-checked; bad cells are skipped and reported by row/column.
  Attributes the file omits get their definition's default.
- A bad cell does **not** stop the import: the contact is still written, only that cell is skipped and listed (row, column, why). Rows with no phone number are skipped.
- Re-importing never overwrites a value someone set by hand in the CRM.
- 10 MB limit.

## Assign

`ck contacts assign` chooses contacts (by `--phones a,b` or by the same filters
as `list`) and a target — **exactly one** of:

```bash
# into a workflow
ck contacts assign --phones 919812345678 --workflow <workflowId> [--name "Test run"] [--at <ISO>] [--window 10:00-19:00] [--carry-over] [--priority n] [--force]

# preview first: who would be assigned, where, and which --phones are not contacts. Starts nothing.
ck contacts assign --phones 919812345678 --workflow <workflowId> --dry-run

# straight to a voice agent (a call run)
ck contacts assign --attr stage=new --agent <agentId> [--language en] [--at <ISO>] [--window 10:00-19:00] [--retries 2] [--gaps 30,60]
```

- **Always `--dry-run` first**: it shows the target, how many contacts match, a sample, and any `--phones` that are not contacts (a real assign silently skips those). It starts nothing.
- With **no** `--phones` and no filters it asks before assigning *every* contact. Don't bypass that.
- Workflow: contacts **currently running** in it are **skipped** (the output says how many; nothing starts and it is not reported as a success); `--force` restarts them. A contact whose earlier run has **finished** is enrolled again normally.
- A selection is capped server-side; the output says when it was truncated — narrow the filters to cover the rest.
- The workflow must have steps; a workflow with an empty graph is refused.
- This **starts real calls / WhatsApp sends**. Say how many contacts and which workflow/agent, and get a yes.

## Export

```bash
ck contacts export --attr stage=qualified --file qualified.csv           # direct download (≤ 5000 rows)
ck contacts export --created-from 2026-10-01 --email me@x.com           # big set → emailed
```

`--fields phone_number,city,stage` limits the columns (base fields and/or attribute names).
