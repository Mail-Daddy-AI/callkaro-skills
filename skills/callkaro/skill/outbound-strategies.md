# Outbound Phone Number Strategies
<!-- graph-summary: Outbound phone number strategies (Rolling Strategy in the dashboard): an ordered list of up to 10 numbers with working hours, days and daily limits that an agent dials from instead of one outbound number; how each call picks its number, the fallback to the outbound number, ck outbound-strategies commands, assigning to agents, and the rule that edits apply to every agent on the strategy. -->

A strategy is a saved, ordered list of the account's own numbers. An agent on a
strategy picks its caller ID per call from that list instead of always using its
single outbound number. Use it to spread volume across numbers (less spam
flagging) and to reach a lead from a different number on each retry.

## How each call picks a number

For every call, retries included, the first number in the list that:
1. is **open now**: inside its working hours (IST) on one of its days, and
2. is **under its daily limit** (`dailyCap`, counted per number per day across
   every strategy that contains it), and
3. **has not called this lead yet**.

After every number has called the lead, `endOfStack` decides:
`loop` (start again from the top), `last` (keep using the last number),
`least` (the number with the fewest calls today).

**Fallbacks** — tell the user these when they matter:
- No number open or under its limit → the call uses the agent's **outbound
  number** (`ck agents set-outbound`). Make sure every agent on a strategy also
  has one.
- A `preferred_did_number` sent with a call wins over the strategy.
- Accounts that are not business-verified always call from CallKaro's default
  number; strategies have no effect until verification.
- Browser test calls don't use the strategy.
- Batch calls: the first attempt per contact uses the outbound number; retries
  use the strategy.

## Rules the server enforces

- Name required (≤ 80 chars); 1–10 numbers; a number only once.
- Numbers must be on the account and not spam, released or unrented — get ids
  from `ck numbers list` ([Phone Numbers](numbers.md)); never invent one.
- Per number: `allDay` (default true) or `from`/`to` as `HH:mm` (from > to is an
  overnight window, e.g. 21:00–02:00); `days` 0–6 with **0 = Monday**, at least
  one; `dailyCap` a whole number ≥ 1 or null (unlimited).
- `endOfStack`: `loop` (default), `last` or `least`.

## Commands

| Command | What it does |
|---|---|
| `ck outbound-strategies list [--json]` | Every strategy: name, id, numbers, end option, agents on it. |
| `ck outbound-strategies get <strategyId> [--json] [--file s.json]` | One strategy with each number's hours (IST), days and daily cap. `--file` saves `{name, endOfStack, numbers}` to edit and send back with `update --set @s.json`. |
| `ck outbound-strategies create --name <name> --numbers <list> [flags]` | Create. |
| `ck outbound-strategies update <strategyId> [flags]` | Change only what you pass; the rest is kept. Applies to **every agent on it**. |
| `ck outbound-strategies assign <strategyId> --agents <ids>` | Exactly these agents (others on it are taken off). |
| `ck outbound-strategies assign <strategyId> --add <ids> / --remove <ids>` | Add or take off agents, keeping the rest. An agent is on one strategy at most, so adding moves it off any other. |
| `ck outbound-strategies delete <strategyId> [--yes]` | Delete. Its agents go back to their outbound number. |
| `ck agents set-outbound-strategy <agentId> --strategy <strategyId>` / `--clear` | Put one agent on a strategy, or take it off. |

Flags on `create` / `update`:
- `--numbers` — comma-separated number ids or phone numbers, in dialling order
  (1–10). On update, numbers already in the strategy keep their settings and
  new ones get the defaults (all day, every day, no cap).
- `--end-of-stack loop|last|least`
- `--hours all-day|HH:mm-HH:mm`, `--days mon-fri|mon,wed,fri|weekends|all`,
  `--daily-cap <n>|none` — applied to **every** number.
- `--set <json|@file.json>` — `{ name, endOfStack, numbers: [{ phoneNumber,
  allDay, from, to, days, dailyCap }] }` for different settings per number.

MCP has the same through `get_outbound_phone_number_strategy_info`,
`create_or_update_outbound_phone_number_strategy`,
`assign_outbound_phone_number_strategy` and
`delete_outbound_phone_number_strategy`; an agent's strategy is its
agent-level `phoneNumberStrategyId` (also settable with
`ck agents update <agentId> --set '{"phoneNumberStrategyId":"<id>"}'`).

## Typical flow

```bash
ck numbers list --json                           # pick 2+ owned, non-spam numbers
ck outbound-strategies create --name "Daytime rotation" \
  --numbers 9179xxxxx463,9179xxxxx519 --hours 10:00-19:00 --days mon-sat --daily-cap 150
ck agents set-outbound <agentId> --number <id>   # fallback number, if the agent has none
ck outbound-strategies assign <strategyId> --add <agentId>
```

Before editing or deleting a strategy, check `ck outbound-strategies list` for
the agents on it and confirm with the user: the change hits all of them at once,
including live ones.
