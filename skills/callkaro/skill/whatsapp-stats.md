# WhatsApp Campaign & Template Stats
<!-- graph-summary: Read-only WhatsApp stats: list campaigns and their status/send counts, one campaign's delivery/read/reply/click totals and daily series, and template link-click stats. Sending, cancelling and template changes are not available here. -->

Read-only. Sending, cancelling or exporting a campaign and creating or editing
templates stay on the dashboard. WhatsApp **numbers** are in [Phone Numbers](numbers.md).

## Commands

| Command | What it shows |
|---|---|
| `ck whatsapp campaigns [--status s] [--page n] [--page-size ≤100] [--json]` | Campaigns newest first: id, template, status (`scheduled queued sending completed failed cancelled`), recipients / sent / failed, created. |
| `ck whatsapp campaign <id> [--json]` | Totals: messages, sent/delivered, read, failed, **repliers** (people who replied after receiving it), link clicks and unique clickers. |
| `ck whatsapp campaign-daily <id> [--days 1-90 \| --start YYYY-MM-DD --end YYYY-MM-DD] [--json]` | Day-by-day sent, delivered, read, failed, replied and clicks (IST days). Default: last 7 days. |
| `ck whatsapp template-clicks [templateName] [--page n] [--page-size ≤100] [--json]` | No name: one row per template (total clicks, unique recipients, last click). With a name: per-recipient clicks for that template. |

MCP equivalents: `list_whatsapp_campaigns`, `get_whatsapp_campaign_analytics`,
`get_whatsapp_campaign_timeseries`, `get_whatsapp_template_click_stats`.

## Reading the numbers

- Start from `campaigns` to get the id; every other command takes it.
- `read` counts against **sent**, replies against **sent**, failures against **messages**.
- An **unknown campaign id returns all zeros**, not an error. If a campaign you know
  should have data shows zeros, re-check the id with `ck whatsapp campaigns`.
- `recipients` / `sent` / `failed` on the list are the dispatch counts recorded when
  the campaign was sent; `campaign` analytics are counted from the message log, so
  they keep moving as statuses and replies arrive.
- Link-click numbers only exist for campaigns sent with click tracking on.
- The recipient-file link stored on a campaign is never shown.
