# KPI Report Format
<!-- graph-summary: The JSON format of a KPI report for ck kpi report save and the MCP save tool: elements (charts, tables, text), chart types and their axes, variable refs and bases, compare with previous period, text style, ${token} text, custom variables, page style (UI features), layout and limits, with two complete examples. -->

A KPI report is a set of A4 pages holding **elements**: charts, tables and text.
You write one as JSON and save it with `ck kpi report save` (MCP:
`save_kpi_report`). See [KPI Manager](kpi-manager.md) for the commands and the
schedule.

```json
{
  "name": "Daily summary",
  "custom_variables": [],
  "elements": [ { "type": "chart", "chart_type": "tiles", "refs": ["builtin:total_calls"] } ]
}
```

`page_count` and `page_style` are optional. Leave out `x`, `y`, `w` and `h` and
`save` stacks each element full width down the pages, adding pages as needed.
Elements you have positioned stay where they are, and new ones go below them.

## Variable refs

A ref is `<kind>:<id>[#<base>]`. **Run `ck kpi report variables <agentId>`
first** and use only refs it lists, or custom variables you define. Never
invent one.

| Kind | Example | Value |
|---|---|---|
| `builtin` | `builtin:connected_pct` | Built-in call numbers: counts, %, latency and cost in credits (`total_latency_p95`, `cost_sum`, `cost_per_call`…), and two lists (`hangup_reasons`, `drop_off_reasons`) |
| `postcall` | `postcall:interested#connected` | A value breakdown of a post-call variable |
| `custom` | `custom:hot_lead#unique` | A count of calls matching a custom variable defined in this report |
| `metric` | `metric:Lead to sale` | A KPI metric's actual vs target |
| `source` | `source:crm.data.conversion_rate` | A data-source field, read directly |

**Bases** (what to count): `all` (default, omit `#all`), `connected`,
`converted`, `unique` (unique receipts), `unique_connected`. Post-call refs
take every base except `converted`.

## Elements

### Charts: `{ "type": "chart", "chart_type", "title"?, "refs" }`

| `chart_type` | Shows | Axes `save` picks from `refs` |
|---|---|---|
| `tiles` | one number tile per ref | — |
| `bar` | bars | 1 list/post-call ref → its values on X; else `x_axis: "metrics"` (one bar per ref) |
| `line` | a trend | `x_axis: "dim:time_hour"` |
| `pie` | slices (one measure) | 1 list/post-call ref → its values; else one slice per ref |
| `funnel` | steps, one per ref | no X; `options.direction`: `horizontal`/`vertical` |
| `table` | a data table | like `bar` |

**Compare with the previous period:** `"options": { "compare_previous": true }` on a
`tiles` chart.
- **What it shows:** each tile shows the change against the window just before the
  report's window, of the same length. A report for 08:00–12:00 compares with 04:00–08:00.
- **How it looks:** in the dashboard as ▲/▼, in the PDF and email as `+12 vs previous` in
  green or `-3 pts vs previous` in red. Percentages change in points (`pts`).
- **Which tiles:** built-in numbers, cost & latency, and custom variables. Post-call
  breakdowns, reason lists, data-source fields and KPI metrics show no change.
- **Cost:** it adds one extra query per report. The dashboard has no switch for it, so
  set it here.

To control the axes yourself, set `x_axis` and `y_axis` (and `stack_by` for bar
and line):
- **`x_axis`:** `metrics`, `dim:time_hour`, `dim:time_day`, `dim:hangup_reason`,
  `dim:drop_off_reason`, `dim:is_connected`, `dim:converted`, `dim:direction`,
  `dim:postcall:<name>` or `dim:metadata:<key>`.
- **`y_axis`:** the measure refs, e.g. `["builtin:total_calls"]`.

A pie takes one `y_axis` ref.

### Table: `{ "type": "table", "cells": [["Metric", "Value"], ["Connected", "${connected_pct}"]], "header": true }`

At most 30 rows × 8 columns, and 500 characters per cell.

### Text: `{ "type": "text", "content": "…", "style"? }`

- `content` holds up to 5,000 characters.
- `style` is `{ "size": 8-72, "color": "#rrggbb", "align": "left|center|right", "bold": true|false, "italic": true|false, "underline": true|false }`.
- **Defaults:** size 14, color `#111827`, left-aligned, and bold, italic and underline off.
- **In the PDF:** all of these print, including underline.

### `${token}` in text and table cells

`${connected_pct}` inserts a built-in (the `builtin:` prefix is optional),
formatted as in the PDF: percentages already end in `%`.
Other refs keep their kind: `${postcall:interested#connected}`,
`${custom:hot_lead}`, `${metric:Lead to sale}`.

## Custom variables

Custom variables are defined in the report and counted with `custom:<name>[#base]`:

```json
{ "name": "hot_lead", "mode": "expression", "expression": "is_connected && post_call.interested == 'yes'",
  "equals": true, "consider_for": ["unique"] }
```

- **`name`:** lowercase snake_case, unique in the report.
- **`consider_for`:** the base(s) to count. Use one of them in the ref.
- **Test first:** run every expression through
  `ck kpi report check-expression <agentId> '<expr>'` before saving.
- **Conditions mode:** variables made in the dashboard can use `"mode": "conditions"`.
  When editing a report, keep those exactly as `get` returned them.

## Page style (the UI features panel)

`page_style` is optional. Leave it out to get the defaults.

```json
"page_style": { "background": "#fbfaf8", "shadow": true, "page_numbers": true, "grid": true,
                "grid_size": 24, "snap_to_grid": true, "smart_guides": true, "margin_guide": false }
```

| Key | Default | What it does |
|---|---|---|
| `background` | `#ffffff` | Page colour, printed in the PDF. Dashboard swatches: `#ffffff`, `#fbfaf8`, `#f6f7f9`, `#f3f0fa`, `#eef6f3`, `#fdf4e7`, `#fdeeee`, `#e9edf5`, `#1f2937`; any `#rrggbb` works. On the dark `#1f2937`, set light text colours. |
| `page_numbers` | `true` | "Page N" at the bottom right of each sheet in the dashboard editor. The PDF does not print page numbers. |
| `shadow` | `true` | A shadow under the sheet in the editor. |
| `grid` | `true` | Editor-only grid, never printed. |
| `grid_size` | `24` | Grid spacing in pixels: 8, 12, 16, 24, 32 or 48. |
| `snap_to_grid` | `true` | Drag, drop and resize land on grid lines in the editor. |
| `smart_guides` | `true` | Alignment lines and snapping while dragging in the editor. |
| `margin_guide` | `false` | Shows the 40px page margin in the editor, never printed. |

Only `background` changes the PDF. The other keys change only how the dashboard editor
looks.

## Limits

| Limit | Value |
|---|---|
| Items per report | 40 |
| Refs per chart | 12 |
| Custom variables per report | 30 |
| Pages per report | 30 |
| Reports per agent | 20 |
| Report name | 60 characters |

The page is 794 × 1123 (A4 at 96 dpi). `y` is measured from the top of page 1,
so page 2 starts at 1123.

## Example: daily summary

```json
{
  "name": "Daily summary",
  "elements": [
    { "type": "text", "content": "Daily calling summary", "style": { "size": 24, "bold": true } },
    { "type": "chart", "chart_type": "tiles", "title": "Today",
      "refs": ["builtin:total_calls", "builtin:connected_pct", "builtin:converted_pct", "builtin:cost_per_call"] },
    { "type": "chart", "chart_type": "line", "title": "Connectivity by hour", "refs": ["builtin:connected_pct"] },
    { "type": "chart", "chart_type": "bar", "title": "Why calls ended", "refs": ["builtin:hangup_reasons"] },
    { "type": "text", "content": "Connected ${connected_pct} of ${total_calls} calls; P95 latency ${total_latency_p95}s." }
  ]
}
```

## Example: interest funnel by post-call variable

```json
{
  "name": "Interest funnel",
  "custom_variables": [
    { "name": "interested", "mode": "expression", "expression": "post_call.interested == 'yes'",
      "equals": true, "consider_for": ["unique"] }
  ],
  "elements": [
    { "type": "chart", "chart_type": "funnel", "title": "Funnel",
      "refs": ["builtin:unique_receipts", "builtin:unique_connected", "custom:interested#unique", "builtin:unique_converted"] },
    { "type": "chart", "chart_type": "pie", "title": "Interest (connected calls)", "refs": ["postcall:interested#connected"] }
  ]
}
```

Replace `interested` with a post-call variable that `report variables` lists for the agent.
