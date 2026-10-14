# Workflows + Contacts together

Contacts are **who**; a workflow is **what happens to them**. They meet in
three places, and getting these right is most of the work:

| Meeting point | How |
|---|---|
| **Attributes feed the graph** | A Conditions branch or a WhatsApp template parameter with `source: "contact"` reads a CRM attribute **by its `name`**; the contact's data personalises each run |
| **The graph writes attributes back** | An `update-lead` node sets attributes on the contact (`static_value`, or a value from the last call: `post_call_variables`, `hangup_reason`, …) |
| **Enrolment** | `ck contacts assign --workflow <id>` starts one run per contact |

Read [workflows.md](workflows.md) and [contacts.md](contacts.md) for the
commands; this file is the order of operations.

## End-to-end: "call new leads, WhatsApp the ones who don't answer, mark them"

```bash
ck whoami

# 1. DEFINE the attributes the workflow will read or write — first, because the
#    graph and the import both refuse names that don't exist.
ck contacts attributes list --json
ck contacts attributes set stage --type enum --options new,contacted,no_answer,qualified
ck contacts attributes set first_name --type string

# 2. GATHER real ids — never invent agentIds, template ids, number ids.
ck agents list --json                      # agentId for Send Call (prefer agentStatus "live")
ck whatsapp list --json                    # phoneNumberId + display number for WhatsApp nodes
ck chat-agents templates --json            # template id / name / language / status (use APPROVED)
ck chat-agents template <templateId> --json   # its variables[].id = the exact parameters[].key values
ck contacts attributes list --json         # CRM attribute names for update-lead / contact conditions
ck agents get <agentId> --json             # publishedVersionId
ck agents get <agentId> --versions <publishedVersionId> --json   # postcall[].name = post_call_variables fields (skip type call_drop_off_reason)

# 3. BUILD the graph from those listings only, then check it.
#    Start → Send Call → Conditions(connected_call) →
#       connected:  Update Contact(stage=contacted) → End
#       otherwise:  Send WhatsApp Template → Update Contact(stage=no_answer) → End
ck workflows validate --file graph.json      # repeat until clean
ck workflows create "New-lead follow-up" --file graph.json
ck workflows get <workflowId> --json         # read back

# 4. LOAD contacts (header must be phone_number; other columns = defined attributes)
ck contacts upload leads.csv
ck contacts list --attr stage=new --json     # confirm who is in

# 5. TEST on ONE number first. Preview, then (with the user's yes — this places a
#    real call and a real WhatsApp message) run it for real.
ck contacts assign --phones 9198XXXXXXXX --workflow <workflowId> --dry-run
ck contacts assign --phones 9198XXXXXXXX --workflow <workflowId> --name "smoke test"

# 6. VERIFY what actually happened
ck workflows leads <workflowId> --json
ck workflows run <workflowId> 9198XXXXXXXX   # step by step; why it took that branch
ck workflows journey <workflowId> 9198XXXXXXXX
ck contacts get 9198XXXXXXXX                 # did update-lead write stage?

# 7. SCALE, only after the smoke test looked right and the user agrees. Preview the
#    count first — --dry-run says exactly how many contacts the filter selects.
ck contacts assign --attr stage=new --workflow <workflowId> --dry-run
ck contacts assign --attr stage=new --workflow <workflowId> --window 10:00-19:00 --name "Oct batch"
```

## Rules for doing this safely

1. **Attributes first, then graph, then contacts.** Out of order, each step fails
   on a name that doesn't exist yet.
2. **Use attribute `name`, not the display label** in `update-lead`, `contact`
   conditions and template parameters. `ck contacts attributes list --json` shows both.
3. **Enum attributes only accept their listed options.** An `update-lead` writing
   `"won"` to an enum without `won` is skipped for that contact. Add the option
   first (`attributes set stage --options …` — list **all** options you want to keep).
4. **Always `--dry-run` first, then smoke-test with `--phones` on one number**, read the run with
   `ck workflows run`, and only then assign by filter. Assigning places real
   calls and sends real WhatsApp messages; state the count and the workflow
   and wait for a yes.
5. **Re-assigning skips contacts already running** in the workflow; once their run has finished they can be enrolled again. To restart one that is still running use `--force`; don't use `--force` on a big filter.
6. **Update Contact can't overwrite a hand-set value.** An attribute someone set by
   hand (`ck contacts update`, `create --attr`, the dashboard) is protected from
   workflow writes. Load test data with `upload` (or leave the attribute unset)
   rather than `contacts update`, or the node will appear to do nothing — see
   [contacts.md](contacts.md) § Hand-set values.
7. **A graph is validated on every save**, but validation can't know your
   business logic — read the graph back (`get --json`) and walk each branch to an End.
8. **Don't edit a workflow with leads running** without asking: this pack has
   not verified how in-flight runs react.

## Finding and acting on outcomes

The graph's `update-lead` nodes turn outcomes into attributes, and contacts can
be filtered by them — so follow-ups are just another assign:

```bash
ck contacts list --attr stage=no_answer --json                 # who didn't pick up
ck contacts export --attr stage=qualified --file hot.csv       # hand-off list
ck contacts assign --attr stage=no_answer --workflow <retryWorkflowId> --name "Second attempt"
```

## Debugging

| Symptom | Look at |
|---|---|
| `create`/`update` rejected | The error lists each problem with a `nodeId`; `ck workflows validate --file …` shows them all at once |
| Upload refused | "not a defined attribute" → `contacts attributes set …`, or `--ignore-unknown` |
| Lead stuck / went the wrong way | `ck workflows run <id> <phone> --json` — the step statuses, the handle taken, and the variables the Conditions node tested |
| Attribute wasn't updated | The value was **set by hand** (protected — `contacts get --json` shows `source: manual`), or the attribute is undefined, or the value is outside an enum; `run <id> <phone> --json` shows the `update-lead` step |
| Contact "not in workflow" after assign | Already running there (skipped) — see the assign output; `--force` to restart |
| Template node sends nothing | `ck chat-agents templates` → `status` must be `APPROVED`, and every `parameters[].key` must be one of `ck chat-agents template <id>`'s `variables[].id` |
