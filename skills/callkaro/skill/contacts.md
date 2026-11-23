<!-- graph-summary: CRM contacts: attribute schema, CSV import, hand-set protection, assigning to an agent or workflow (done by the user on the dashboard). Use when managing leads or the fields a workflow or agent reads. -->
# Contacts (CRM)

A contact is a **phone number plus attributes**. Attributes are fields the
account **defines first** (name, type, optional allowed values); contacts can
only hold attributes that have a definition. Workflows read and write these
same attributes — see [workflows-and-contacts.md](workflows-and-contacts.md).

## Ground rules

1. **Define an attribute before using it.** Import and update refuse a name
   with no definition (naming the offenders) instead of dropping data silently.
2. **Use phone numbers as digits with country code** (`919812345678`, no `+` or
   spaces) — imports and attribute updates strip non-digits, so this is the form
   everything else will match.
3. **Assigning contacts places real calls or sends real messages** — see
   [Assign](#assign). Confirm with the user first; test on one number.
4. **Destructive:** deleting a contact or an attribute. Only with the user's say-so.

## On the dashboard

The user browses, creates, updates, deletes, imports, exports and assigns
contacts on the CallKaro dashboard; there is no harness tool for contacts.

- **Browse/filter** by search, channel, attribute value, last message state
  (read, delivered, sent, failed, clicked, not_clicked), created/updated dates
  (IST), or assigned-to-me.
- **Create** a contact with a phone number, or merge into an existing one.
- **Update** sets or clears attributes, validated against the definitions.
- **Export** downloads up to 5000 rows directly; a larger set is **emailed**.
  The columns can be limited to base fields and/or attribute names.
- **Attribute definitions** have a name, type, label, description, enum options
  and flags. Editing an existing attribute changes only what you change.
  Deleting one is a soft delete: values on contacts are kept but hidden.

Attribute types: `string description enum number date boolean datetime time array object`.
`enum` needs options. Flags: manual-only (stops AI/functions overwriting it) or
AI-updatable; required or optional; hidden or visible; a default mode (drop,
type default, or a custom value).

## Attributes

Changing an enum's options replaces the list — keep **all** the options you want.

Values entered as text are coerced by the attribute's type (`true/yes/1` for
boolean, ISO or common formats for dates). A value that doesn't fit is
**refused with the reason**, not guessed. An empty value removes it.

### Hand-set values are protected from workflows

A value set by a person — creating or updating a contact by hand on the
dashboard — is marked **manual**, and **automated writes will not
overwrite it**: a workflow's Update Contact node, an agent's post-call update, and
CSV re-imports all skip an attribute whose current value was set by hand (verified:
a workflow marked a CSV-imported contact `won` but left a hand-edited one at
`contacted`). Only another manual edit changes it. So don't pre-set, by hand, an
attribute a workflow is meant to update; and if one "didn't update", check how its
value was last set (the attribute's `source` on the contact).

## Import (CSV)

```csv
phone_number,name,city,stage
919812345678,Jatin,Delhi,new
919811111111,Asha,Mumbai,contacted
```

- Header row required, and the phone column must be named **`phone_number`**
  (unlike batch CSVs, where it is simply column 1).
- Every other column must match a defined attribute (case-insensitive). Unknown
  columns **refuse the whole file**, listing them — define them first, or
  remove those columns.
- Cells are type-checked; bad cells are skipped and reported by row/column.
  Attributes the file omits get their definition's default.
- A bad cell does **not** stop the import: the contact is still written, only that cell is skipped and listed (row, column, why). Rows with no phone number are skipped.
- Re-importing never overwrites a value someone set by hand in the CRM.
- 10 MB limit.

## Assign

Assigning chooses contacts (by phone numbers or by the same filters as
browsing) and a target — **exactly one** of: a workflow (optionally a run name,
start time, daily calling window, carry-over, priority) or a voice agent as a
call run (optionally language, start time, window, retries and gaps).

- **Check the count first**: confirm with the user who is targeted and how many contacts match. Phone numbers that are not contacts are silently skipped by a real assign.
- With **no** phone numbers and no filters, an assign targets *every* contact: never let that happen without the user's explicit yes.
- Workflow: contacts **currently running** in it are **skipped** (nothing starts for them and it is not a success); forcing restarts them. A contact whose earlier run has **finished** is enrolled again normally.
- Contacts enrol into the workflow's **live version**, and each run stays on the version it started on.
- A selection is capped server-side; the result says when it was truncated — narrow the filters to cover the rest.
- The workflow must have steps; a workflow with an empty graph is refused.
- This **starts real calls / WhatsApp sends**. Say how many contacts and which workflow/agent, and get a yes.

## Export

Up to 5000 rows download directly; a bigger set is emailed. Limit the columns
to the base fields and attribute names the user needs.
