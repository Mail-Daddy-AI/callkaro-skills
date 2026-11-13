# Chat Audit Strategies (WhatsApp AI Auditor)
<!-- graph-summary: Create and manage AI-auditor strategies for WhatsApp chat agents and run manual audit batches; commands, contact filters, daily limits, and the new-messages-only rule. -->

Like [audit strategies](audit-strategies.md) but for **WhatsApp chat agents**
(`agentId` must be a WhatsApp chat agent). A strategy audits whole
conversations (customer + agent number) against free-text instructions. Active
strategies run once a day at 5 AM IST; each run audits only messages since the
conversation's last audit, clear, or handover.

## Commands (`ck chat-audit-strategies`, alias `ck chat-audit`)

| Command | What it does |
|---|---|
| `list <agentId>` / `get <agentId> <strategyId>` | Check existing strategies before creating. |
| `models <agentId>` | Models chat audits may use. Never invent one. |
| `create <agentId> --strategy <text> [flags]` | Needs `--pct-per-day` or `--max-per-day` (not both 0). Inactive unless `--active`. |
| `update <agentId> <strategyId> [flags]` | Only named fields change. `--set` keys (`audit_filters`, `extra_variables`, `llms`) each replace the stored value. |
| `delete <strategyId>` | Permanent. |
| `batch <agentId> <strategyId> --max <n> [--phone <n>] [--model <name>] [--set <json>]` | Audit up to n conversations now (1-500, uses credits). `--set` takes `filters`, `minUserMessages`, `minMessages`. |

**Chatflow summary.** The auditor does not read the agent's prompt or published
version. It judges each conversation against the strategy's `--strategy` text and
its `--chatflow-summary`: how the conversation should go (stages in order,
actions the agent must take, follow-up and hand-off rules, the intended outcome).
Write it for the flow being audited; without one the auditor has no agent
context, so set it on every strategy. It is optional (max 40,000 chars), is kept
when an update omits it, and is cleared with `--set '{"chatflow_summary":""}'`.
MCP: `chatflow_summary` on `create_or_update_chat_audit_strategy`.

`audit_filters` are contact filters: `contact_created_from/_to`,
`contact_updated_from/_to` (YYYY-MM-DD, inclusive) and
`attributes: {name: value | [values]}`. Get the attribute names and their allowed
values (enum options) from `ck contacts attributes list` (MCP: `list_contact_attributes`),
and ask the user which attribute and value to filter on — never guess them.

`batch` answering "No new conversations to audit for these filters" is normal:
every matching conversation was already audited up to its latest message.

## Reading results (read-only)

`<id>` is a **batch id** by default; add `--by-strategy` for a **strategy id**.
`--from/--to` are `YYYY-MM-DD` (India days).

| Command | What it shows |
|---|---|
| `batches [--agent id] [--from d --to d] [--page n]` | Audit batches, newest first: strategy, agent, status, trigger, chats audited, average score, cost. **Start here for a batch id**, including the one `batch` just created. |
| `strategy-reports [--agent id] [--from d --to d]` | The same rolled up per strategy. |
| `report <id> [--by-strategy]` | Scores, chats below 80, credits per chat, issues by severity and by dimension. |
| `audits <id> [--by-strategy] [--status s] [--sort s] [--page n]` | The conversations audited: contact number, status, overall / chatflow / function / system scores, issue count, top problem. |
| `audit <auditId>` | One conversation audit in full; `--json` has the issues and the audited messages. |

All take `--json` / `--file`. MCP: `list_chat_audit_batches`,
`list_chat_audit_strategy_reports`, `get_chat_audit_report`, `list_chat_audits`,
`get_chat_audit`.

MCP equivalents: `get_chat_audit_strategy_setup_info`,
`create_or_update_chat_audit_strategy`, `delete_chat_audit_strategy`,
`create_chat_audit_batch`.
