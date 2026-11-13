# Embed Widgets
<!-- graph-summary: Embed widgets put an agent on a website or app: the chat, omni and voice types and which agent each needs, ck widgets commands, omni settings (chips, pre-chat, history, voice agent, Call us teams, launcher), install code, and the rule that edits go live on every embed. -->

A widget puts one agent on a website or app. Customers paste a script tag
(or open a link in a web view) once; later edits go live without touching
their site again.

| Type | Visitor gets | `--agent` must be |
|---|---|---|
| `chat` | Chat page, opened as a link in an app or web view | a published chat agent on the **Widget / App** channel |
| `omni` | Chat panel on a site, plus optional voice agent and **Call us** callback teams | a published **AI** chat agent (`ai`, `advanced` or `workflow` mode — not a flow agent) |
| `voice` | Talk-to-agent button | a voice agent |

The type is fixed at creation. To change it, create a new widget. Find agent
ids with `ck chat-agents list` / `ck agents list` ([Chat agents](chat-agents.md),
[Voice Agents](voice-agents/agent-overview.md)); never invent one.

## Commands

| Command | What it does |
|---|---|
| `ck widgets list [--json]` | Every widget: name, id (`wgt_…`), type, agent, status. |
| `ck widgets get <widgetId> [--json] [--file w.json]` | Full settings plus install code. `--file` saves JSON to edit and send back. |
| `ck widgets create --type <chat\|omni\|voice> --agent <id> [flags] [--set <json>]` | Create, and print the install code. |
| `ck widgets update <widgetId> [flags] [--status active\|paused] [--set <json>]` | Change only the named fields. |
| `ck widgets delete <widgetId> [--yes]` | Delete. It stops working everywhere it is embedded and open chats are closed. |
| `ck widgets logo <widgetId> <file>` | Upload a logo (.png, .jpg, .webp, .svg, max 2MB). |
| `ck widgets install <widgetId> [--json]` | Print the script tag and/or link. |

Flags on `create`/`update`: `--name`, `--bot-name`, `--greeting`,
`--primary-color #hex`, `--secondary-color #hex`, `--domains
example.com,*.example.com` (empty = any site), `--logo-text` (omni).

`--set` takes any other field: `settings` (omni), `position`
(`bottom-right`/`bottom-left`, voice and chat), `languages`, `dailyMinutes`
(0 = no cap) and `maxCallSeconds` (0 or 30-1800) for voice.

MCP has the same through `get_widget_info`, `create_or_update_widget` and
`delete_widget` (no logo upload; use the dashboard).

## Omni `settings`

```json
{
  "chips": ["Where's my order?", "Talk to sales"],
  "preChat": { "phoneRequired": true },
  "history": { "enabled": true, "limit": 5 },
  "files": true,
  "stt": true,
  "voice": { "enabled": true, "agentId": "<voice agent id>" },
  "callUs": { "enabled": true, "teams": [
    { "title": "Sales", "subtitle": "Mon-Sat, 10-7", "phoneNumber": "919876543210", "agentId": "<voice agent id>" }
  ] },
  "branding": { "whiteLabel": false, "name": "" },
  "trigger": { "position": "right", "cta": "Chat with us", "draggable": false,
               "bg": "#18181b", "fg": "#ffffff", "icon": "chat", "radius": 26 }
}
```

- `chips`: at most 7, 60 characters each. `history.limit`: 3, 5, 10 or 20.
- `trigger.icon`: chat, msg, phone, wave, mic or bag. `trigger.radius`: 0-30.
- Turning `voice` or `callUs` on needs a voice agent id (and at least one
  team, at most 6). Every id must be a voice agent of this account.
- On update, `settings` merges onto the saved settings key by key, but a list
  (`chips`, `callUs.teams`) replaces the saved list. Keep a team's `id` when
  editing it.

## Install

| Type | Install code |
|---|---|
| omni | `<script src="https://widget.callkaro.ai/omni-widget.js" data-ck-id="<id>" defer></script>`, or the link `https://widget.callkaro.ai/omni.html?w=<id>` in a web view |
| chat | the link `https://widget.callkaro.ai/chat.html?w=<id>`, opened in an in-app browser or web view |
| voice | `<script src="https://widget.callkaro.ai/w.js" data-ck-id="<id>" defer></script>` |

The script goes before `</body>`. If `allowedDomains` is set, the widget only
loads on those hosts, so add every site (and `localhost` for testing) first.

## Rules

- `ck widgets get` before `update`; send whole lists.
- An update on an `active` widget changes it for live visitors at once.
  Confirm with the user first. To try changes safely, create a second widget
  and test on that. `--status paused` switches the widget off for visitors; it
  is not a draft mode.
- Confirm before `delete`.
- Creating and changing widgets needs an active Widgets subscription; a 403
  about the subscription means the user must subscribe in the dashboard.
