<!-- graph-summary: How contacts and workflows connect: enrolment, the data a workflow reads from the CRM, and writing results back. Use when a workflow must act on contact attributes or update them. -->
# Workflows + Contacts together

Contacts are **who**; a workflow is **what happens to them**. They meet in
three places, and getting these right is most of the work:

| Meeting point | How |
|---|---|
| **Attributes feed the graph** | A Conditions branch or a WhatsApp template parameter with `source: "contact"` reads a CRM attribute **by its `name`**; the contact's data personalises each run |
| **The graph writes attributes back** | An `update-lead` node sets attributes on the contact (`static_value`, or a value from the last call: `post_call_variables`, `hangup_reason`, …) |
| **Enrolment** | Assigning contacts to the workflow (on the dashboard) starts one run per contact |

Read [workflows.md](workflows.md) and [contacts.md](contacts.md) for the
details; this file is the order of operations. The user does every step below
on the CallKaro dashboard except where a harness tool is named.

## End-to-end: "call new leads, WhatsApp the ones who don't answer, mark them"

1. **DEFINE** the attributes the workflow will read or write — first, because the
   graph and the import both refuse names that don't exist (e.g. `stage` as an
   enum `new,contacted,no_answer,qualified`; `first_name` as a string).
2. **GATHER** real ids — never invent agentIds, template ids, number ids:
   `list_agents` (Send Call; prefer a live agent), `list_phone_numbers`
   (WhatsApp `phoneNumberId` + display number), `check_whatsapp_readiness`
   (APPROVED templates; `get_template` → its variables = the exact
   `parameters[].key` values), the CRM attribute names from the user, and
   `read_version` on the published version (`postcall[].name` =
   `post_call_variables` fields; skip type `call_drop_off_reason`).
3. **BUILD** the graph from those listings only:
   Start → Send Call → Conditions(connected_call) →
   connected: Update Contact(stage=contacted) → End;
   otherwise: Send WhatsApp Template → Update Contact(stage=no_answer) → End.
   Saving validates it; fix and repeat until clean, then read it back.
4. **LOAD** contacts (header must be `phone_number`; other columns = defined
   attributes) and confirm who is in.
5. **TEST** on ONE number first: confirm the target, then (with the user's yes — this places
   a real call and a real WhatsApp message) run it for real.
6. **VERIFY** what actually happened: the workflow's leads, that number's run
   step by step (why it took that branch), its journey, and whether
   `update-lead` wrote `stage` on the contact.
7. **SCALE**, only after the smoke test looked right and the user agrees.
   Confirm the count first — how many contacts the filter selects — then assign
   by filter, within a calling window.

## Rules for doing this safely

1. **Attributes first, then graph, then contacts.** Out of order, each step fails
   on a name that doesn't exist yet.
2. **Use attribute `name`, not the display label** in `update-lead`, `contact`
   conditions and template parameters. The dashboard's attribute list shows both.
3. **Enum attributes only accept their listed options.** An `update-lead` writing
   `"won"` to an enum without `won` is skipped for that contact. Add the option
   first (editing the options replaces the list — keep **all** options you want).
4. **Always confirm the count first, then smoke-test on one number**, read its run,
   and only then assign by filter. Assigning places real
   calls and sends real WhatsApp messages; state the count and the workflow
   and wait for a yes.
5. **Re-assigning skips contacts already running** in the workflow; once their run has finished they can be enrolled again. To restart one that is still running, force it; don't force a big filter.
6. **Update Contact can't overwrite a hand-set value.** An attribute someone set by
   hand (creating or editing a contact on the dashboard) is protected from
   workflow writes. Load test data with a CSV import (or leave the attribute unset)
   rather than a hand edit, or the node will appear to do nothing — see
   [contacts.md](contacts.md) § Hand-set values.
7. **A graph is validated on every save**, but validation can't know your
   business logic — read the saved graph back and walk each branch to an End.
8. **Don't edit a workflow with leads running** without asking: this pack has
   not verified how in-flight runs react.

## Finding and acting on outcomes

The graph's `update-lead` nodes turn outcomes into attributes, and contacts can
be filtered by them — so follow-ups are just another assign:

- Who didn't pick up: filter contacts by `stage=no_answer`.
- Hand-off list: export contacts with `stage=qualified`.
- Second attempt: assign `stage=no_answer` to a retry workflow.

## Debugging

| Symptom | Look at |
|---|---|
| Save rejected | The error lists each problem with a `nodeId` |
| Import refused | "not a defined attribute" → define it, or remove the column |
| Lead stuck / went the wrong way | The lead's run: the step statuses, the handle taken, and the variables the Conditions node tested |
| Attribute wasn't updated | The value was **set by hand** (protected — the contact shows `source: manual`), or the attribute is undefined, or the value is outside an enum; the run shows the `update-lead` step |
| Contact "not in workflow" after assign | Already running there (skipped) — see the assign result; force to restart |
| Template node sends nothing | `check_whatsapp_readiness`: the template must be `APPROVED`, and every `parameters[].key` must be one of its variables' ids |
