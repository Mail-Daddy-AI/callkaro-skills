#!/usr/bin/env python3
"""Build a Voice AI Bot QA test workbook from a spec JSON.

Usage:
  python build_testbook.py SPEC.json [--out FILE.xlsx] [--template PATH] [--check-only]

The bundled template workbook carries every style, dropdown, colour rule, formula,
chart and sheet layout of the CallKaro QA framework. This script only swaps in the
bot-specific text and test rows, so formatting and scoring logic never drift.
Needs: openpyxl (pip install openpyxl).
"""
import argparse, copy, json, os, re, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHEETS = {  # sheet name -> (ID prefix, spec key is the sheet name)
    'P1 Technical': 'TEC', 'P2 Call Flow': 'FLW', 'P3 Business': 'BIZ', 'P4 Humanization': 'HUM',
}
FIELDS = ['category', 'parameter', 'verifies', 'method', 'example_input', 'expected', 'type', 'priority']
TYPES = {'Positive', 'Negative', 'Edge'}
PRIOS = {'P0', 'P1', 'P2'}
SPARE_ROWS = 10  # blank pre-formatted rows left under each pillar for the tester to add cases


def load_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def validate(spec, base):
    errs, warns = [], []
    thr = {t['key'] for t in base['_thresholds']} | {t['key'] for t in spec.get('thresholds_extra', [])}
    for sheet in SHEETS:
        rows = spec.get('cases', {}).get(sheet)
        if not rows:
            errs.append(f'{sheet}: no cases in spec'); continue
        seen = set()
        for i, r in enumerate(rows, 1):
            tag = f'{sheet} row {i}'
            for f in FIELDS:
                if not str(r.get(f, '')).strip():
                    errs.append(f'{tag}: missing "{f}"')
            if r.get('type') not in TYPES: errs.append(f'{tag}: type must be one of {sorted(TYPES)}')
            if r.get('priority') not in PRIOS: errs.append(f'{tag}: priority must be one of {sorted(PRIOS)}')
            key = (r.get('parameter') or '').strip().lower()
            if key in seen: warns.append(f'{tag}: duplicate parameter "{r.get("parameter")}"')
            seen.add(key)
            for k in re.findall(r'\[[A-Z0-9_]+\]', f"{r.get('expected','')} {r.get('example_input','')}"):
                if k not in thr: warns.append(f'{tag}: threshold {k} not defined (add to thresholds_extra)')
        have = {r.get('category') for r in rows}
        want = {b['category'] for b in base[sheet]}
        miss = sorted(want - have)
        if miss:
            warns.append(f'{sheet}: baseline categories not covered: {", ".join(miss)} (fine only if truly N/A for this bot)')
        p0 = sum(1 for r in rows if r.get('priority') == 'P0')
        if p0 == 0 and sheet != 'P4 Humanization': warns.append(f'{sheet}: no P0 cases – every pillar should have release-blocking checks')
    return errs, warns


def copy_style(src_cell, dst_cell):
    dst_cell._style = copy.copy(src_cell._style)


def build(spec, template, out):
    wb = openpyxl.load_workbook(template)
    bot = spec['bot']
    refs = {}

    for sheet, prefix in SHEETS.items():
        ws = wb[sheet]
        rows = spec['cases'][sheet]
        tpl = {c: copy.copy(ws.cell(5, c)._style) for c in range(1, 15)}
        old_max = ws.max_row
        total = 4 + len(rows) + SPARE_ROWS
        for r in range(5, max(old_max, total) + 1):
            for c in range(1, 15):
                cell = ws.cell(r, c); cell.value = None; cell._style = copy.copy(tpl[c])
        for i, row in enumerate(rows):
            r = 5 + i; tid = f'{prefix}-{i + 1:02d}'
            vals = [tid] + [row[f] for f in FIELDS]
            for c, v in enumerate(vals, 1):
                ws.cell(r, c).value = v
            for k in re.findall(r'\[[A-Z0-9_]+\]', f"{row['expected']} {row['example_input']}"):
                refs.setdefault(k, []).append(tid)
        for r in range(5, total + 1):
            ws.cell(r, 10).value = f'=IF(I{r}="P0",3,IF(I{r}="P1",2,IF(I{r}="P2",1,0)))'
        if old_max > total:
            blank = wb['Read Me']['A20']._style
            for r in range(total + 1, old_max + 1):
                for c in range(1, 15):
                    cell = ws.cell(r, c); cell.value = None; cell._style = copy.copy(blank)
        ws.auto_filter.ref = f'A4:N{total}'

    # Thresholds: keep the 20 framework rows, append bot-specific rows, rebuild "Referenced by"
    th = wb['Thresholds']
    tstyle = {c: copy.copy(th.cell(5, c)._style) for c in range(1, 6)}
    r = 25
    for t in spec.get('thresholds_extra', []):
        for c in range(1, 6): th.cell(r, c)._style = copy.copy(tstyle[c])
        th.cell(r, 1).value = t['key']; th.cell(r, 2).value = t['controls']
        th.cell(r, 3).value = str(t['recommended']); th.cell(r, 4).value = t['unit']
        r += 1
    for rr in range(5, r):
        ids = refs.get(th.cell(rr, 1).value, [])
        th.cell(rr, 5).value = ', '.join(ids) if ids else '—'
    if spec.get('thresholds_extra'):
        th['A2'].value = ("Numeric bars the pass-criteria refer to (shown in [BRACKETS]). Rows 25+ are bot-specific business constants "
                          "from the source document. Tune the 'Recommended' column per client SLA; keep one bar, one source of truth.")

    # Summary Scorecard run details
    sm = wb['Summary Scorecard']
    sm['B5'].value = bot['name']; sm['B6'].value = bot.get('version', 'v1.0')
    sm['B7'].value = bot.get('use_case', ''); sm['B9'].value = bot.get('tested_by', 'QA team')
    sm['A12'].value = 'ℹ  Clean test suite: result columns K:N are empty. Log Actual Result / Status on the four pillar sheets to activate this scorecard.'

    # Read Me
    rm = wb['Read Me']; short = bot.get('short_name', bot['name'])
    src = bot.get('source_doc', 'the source document')
    rm['A1'].value = f'   {short}  —  Voice Bot QA Test Suite  v1.0'
    rm['A2'].value = '   Test cases built on the CallKaro Voice AI QA Testing Framework (same four pillars, scoring and 95% gate).'
    rm['B5'].value = (bot.get('blurb', '') + f" All test cases are derived from {src}. Cases that depend on rules it does not define are marked (TBD) "
                      "in the expected result – confirm them with the client before certifying.").strip()
    rm['B15'].value = '1.  Copy this workbook for the bot version you are testing and fill in RUN DETAILS on the Summary Scorecard.'
    rm['B16'].value = '2.  This suite ships clean: the Actual / Status / Severity / Remarks columns (K–N) on each pillar sheet are empty. If you re-run a cycle, clear K–N first.'
    rm['B17'].value = '3.  Adapt the Example Input column to your test callers and add any new scenarios as rows (new rows inherit the weights and scoring automatically).'
    extra = bot.get('business_constants_note')
    rm['B29'].value = ('   •  Thresholds — the numeric benchmarks (latency, WER, dead-air…)'
                       + (f' plus this bot\'s business constants ({extra})' if extra and spec.get('thresholds_extra') else '')
                       + ' the pass-criteria refer to; tune per client SLA.')

    # Scoring & Certification worked-example footer
    sc = wb['Scoring & Certification']
    ex = bot.get('blocker_examples', 'a wrong eligibility or business decision, a PII leak, dead air, or a dropped transfer')
    sc['B30'].value = ('This workbook ships with no results logged, so the Summary Scorecard reads NOT YET TESTED until you start a cycle. '
                       f'Typical release blockers for this bot: {ex}.')

    wb.save(out)
    return {s: len(spec['cases'][s]) for s in SHEETS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec'); ap.add_argument('--out'); ap.add_argument('--template')
    ap.add_argument('--check-only', action='store_true')
    a = ap.parse_args()
    spec = load_json(a.spec)
    base = load_json(os.path.join(ROOT, 'references', 'baseline_library.json'))
    errs, warns = validate(spec, base)
    for w in warns: print('WARN ', w)
    for e in errs: print('ERROR', e)
    if errs:
        sys.exit(1)
    if a.check_only:
        print('spec OK'); return
    template = a.template or os.path.join(ROOT, 'assets', 'QA_Framework_Template.xlsx')
    out = a.out or re.sub(r'[^A-Za-z0-9]+', '_', spec['bot'].get('short_name', 'Bot')).strip('_') + '_QA_Test_Suite_v1.0.xlsx'
    counts = build(spec, template, out)
    print('saved', out, counts, 'total', sum(counts.values()))


if __name__ == '__main__':
    main()
