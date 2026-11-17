<!-- graph-summary: Phone numbers: list and assign through the numbers tools, inbound vs outbound rules (inbound is one agent per number); buying, releasing and spam flags are on the dashboard and buying spends credits. Use before assigning a number. -->
# Phone Numbers

Numbers come from CallKaro's own pool (no bring-your-own). A number can be:
- **outbound** for MANY agents (caller ID for outgoing calls)
- **inbound** for exactly ONE agent (the server rejects a second inbound
  assignment with a 409 — surface that message to the user; they release it
  from the other agent first, do not retry with another number)

Load the `numbers` tool group first.

## Tools

| Tool | What it does |
|---|---|
| `list_phone_numbers` (`kind`: `voice` or `whatsapp`) | Your numbers: number, id, spam flag, active/released, which agent uses it inbound, which agents use it outbound. Call it before assigning; never invent an id. |

On the CallKaro dashboard (no tool): the buyable pool and its
`pricepernumber` (₹, deducted from credits); buying a number (**spends
credits** — confirm with the user first); marking or unmarking spam; releasing
a number (unassigned from ALL agents — destructive, confirm first).

## Assigning numbers to agents

`assign_phone_number` (`agentId`, `action`, `phoneNumberId`):

| `action` | What it does |
|---|---|
| `set_voice_outbound` | Set the agent's caller-ID number for outgoing calls. |
| `set_voice_inbound` | Route this number's incoming calls to the agent. Fails with 409 if another agent already has it inbound. |
| `clear_*` | Remove the assignment. |

## Typical flow: give an agent a number

1. `list_phone_numbers` — anything free?
2. None free → the user picks and buys one on the dashboard (after confirming
   the spend).
3. `assign_phone_number` with `set_voice_outbound`; also `set_voice_inbound`
   only if it should answer calls.

An agent needs an **outbound** number before a real call or a batch can
dial from it (test calls may use platform defaults).

## WhatsApp numbers — different pool, no buying

Voice numbers above come from CallKaro's own pool. **WhatsApp numbers do not**
— they come from Meta, via the WhatsApp Business Account the user links **on
the CallKaro dashboard, manually**. Adding a number is Meta's embedded signup
("+ Add Phone Number") — an interactive Facebook-login popup that cannot be
driven headlessly. If the user wants a new WhatsApp number, send them to the
dashboard, then list/assign what's already linked.

Requires an **active WhatsApp subscription** on the account — listing and
assigning WhatsApp numbers return a `SUBSCRIPTION_REQUIRED` /
`SUBSCRIPTION_PAUSED` error otherwise. Surface that message as-is; it means
the dashboard subscription needs activating, not an auth problem.
`check_whatsapp_readiness` checks this.

| Tool | What it does |
|---|---|
| `list_phone_numbers` (`whatsapp`) | Numbers on the linked WhatsApp Business Account, with status/quality. Read-only — the only way to add a new number is the dashboard. |
| `assign_phone_number` (`set_whatsapp_outbound` / `clear_*`) | Set/clear a **voice agent's** WhatsApp outbound number. |

A **voice agent's** WhatsApp inbound number is set on the dashboard; it
unassigns the number from any other agent first (one-agent rule, same as
voice inbound).

For **chat agents**, WhatsApp number assignment is a field on the agent, not a
separate step — see [chat-agents.md](chat-agents.md) (`whatsappPhoneNumber` /
`whatsappDisplayPhN` via `update_chat_agent`).
