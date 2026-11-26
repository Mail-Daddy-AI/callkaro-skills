#!/usr/bin/env python3
"""Render a CallKaro-standard Scope of Work PDF from a spec JSON.

Usage: python build_sow.py SPEC.json [--out FILE.pdf]
Needs: reportlab (pip install reportlab). Fonts, logo and layout live in ../assets.

Layout replicates the reference SoW (Yes Madam v2.0): Letter page, Carlito type,
cover page, Table of Contents, "Purpose" page, then one section per page start with a
navy-header striped table. See ../references/spec_format.md for the spec.
"""
import argparse, json, os, re, sys
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
from reportlab.pdfgen import canvas as rl_canvas

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, 'assets', 'fonts')
LOGO = os.path.join(ROOT, 'assets', 'logo.png')
W, H = 612, 792
LM, RM_X = 68, 569          # text frame: x 68 -> 569
TABLE_W = 470               # tables run 68 -> 538
TXT, GREY, BLUE, NAVY, RULE, STRIPE = (HexColor(c) for c in ('#222222', '#6B7280', '#2E6DA4', '#1B2A4A', '#D9DCE1', '#F4F5F7'))


def fonts():
    for n in ('Regular', 'Bold', 'Italic', 'BoldItalic'):
        pdfmetrics.registerFont(TTFont(f'Carlito-{n}', os.path.join(FONTS, f'Carlito-{n}.ttf')))
        pdfmetrics.registerFont(TTFont(f'Fallback-{n}', os.path.join(FONTS, f'Fallback-{n}.ttf')))
    pdfmetrics.registerFontFamily('Carlito', normal='Carlito-Regular', bold='Carlito-Bold', italic='Carlito-Italic', boldItalic='Carlito-BoldItalic')
    pdfmetrics.registerFontFamily('Fallback', normal='Fallback-Regular', bold='Fallback-Bold', italic='Fallback-Italic', boldItalic='Fallback-BoldItalic')


_CARLITO = None
SYMBOL = {'→': '→', '←': '←', '≥': '≥', '≤': '≤', '≈': '≈', '≠': '≠'}  # drawn with the Symbol font
DING = {'✓': '3', '✔': '3', '✗': '7'}


def _cmap():
    global _CARLITO
    if _CARLITO is None:
        _CARLITO = set(pdfmetrics.getFont('Carlito-Regular').face.charToGlyph)
    return _CARLITO


def rich(text):
    """Escape, apply **bold** / *italic*, and route glyphs Carlito lacks (₹ → ≥ ✓ …) to fallback fonts."""
    t = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', t)
    cm = _cmap(); out = []; b = i = False
    for tok in re.split(r'(<[^>]+>)', t):
        if tok in ('<b>', '</b>', '<i>', '</i>'):
            if 'b' in tok: b = tok == '<b>'
            else: i = tok == '<i>'
            out.append(tok); continue
        for ch in tok:
            if ord(ch) < 128 or ord(ch) in cm or ch in ('&', ';'):
                out.append(ch)
            elif ch in SYMBOL:
                out.append(f'<font name="Symbol">{SYMBOL[ch]}</font>')
            elif ch in DING:
                out.append(f'<font name="ZapfDingbats">{DING[ch]}</font>')
            else:
                face = 'Fallback-' + ('BoldItalic' if b and i else 'Bold' if b else 'Italic' if i else 'Regular')
                out.append(f'<font name="{face}">{ch}</font>')
    return ''.join(out)


def S(name, **kw):
    base = dict(fontName='Carlito-Regular', textColor=TXT, fontSize=10, leading=12)
    base.update(kw)
    return ParagraphStyle(name, **base)


ST = {
    'h': S('h', fontName='Carlito-Bold', fontSize=15, leading=18, textColor=BLUE),
    'body': S('body', fontSize=10.5, leading=13, spaceAfter=9),
    'cell': S('cell'),
    'cellb': S('cellb', fontName='Carlito-Bold'),
    'hdr': S('hdr', fontName='Carlito-Bold', textColor=HexColor('#FFFFFF')),
    'toc': S('toc', fontSize=11, leading=13),
}


class Heading(Flowable):
    """Blue 15pt heading with the thin grey rule under it."""
    def __init__(self, text, key=None):
        super().__init__(); self.p = Paragraph(rich(text), ST['h']); self.key = key; self.text = text

    def wrap(self, aw, ah):
        self.aw = aw; _, h = self.p.wrap(aw, ah); self.h = h
        return aw, h + 10 + 12

    def draw(self):
        top = self.h + 22
        self.p.drawOn(self.canv, 0, 22)
        self.canv.setStrokeColor(RULE); self.canv.setLineWidth(0.5)
        self.canv.line(0, 12 + 0, RM_X - LM, 12 + 0)


class TocLine(Flowable):
    def __init__(self, text, page):
        super().__init__(); self.text = text; self.page = page

    def wrap(self, aw, ah):
        return aw, 21.5

    def draw(self):
        c = self.canv; right = 519 - LM
        c.setFont('Carlito-Regular', 11); c.setFillColor(TXT)
        t = self.text; pg = str(self.page)
        c.drawString(0, 6, t); c.drawRightString(right, 6, pg)
        x0 = pdfmetrics.stringWidth(t, 'Carlito-Regular', 11) + 1
        x1 = right - pdfmetrics.stringWidth(pg, 'Carlito-Regular', 11) - 1
        dot = pdfmetrics.stringWidth('.', 'Carlito-Regular', 11)
        n = int((x1 - x0) / dot)
        c.drawString(x1 - n * dot, 6, '.' * n)


def cell_flowables(content, bold=False, header=False):
    """A cell is a string, or a list of blocks: string paragraphs, {'bullets': [...]}, {'numbered': [...]}."""
    base = ST['hdr'] if header else (ST['cellb'] if bold else ST['cell'])
    blocks = content if isinstance(content, list) else [content]
    items = []  # (text, style, bulletText)
    gap = dict(spaceAfter=4.5)
    for b in blocks:
        if isinstance(b, dict) and 'bullets' in b:
            st = ParagraphStyle('bl', parent=ST['cell'], leftIndent=22, bulletIndent=5, bulletFontName='Carlito-Bold', bulletFontSize=11, **gap)
            items += [(x, st, '\u2022') for x in b['bullets']]
        elif isinstance(b, dict) and 'numbered' in b:
            st = ParagraphStyle('nl', parent=ST['cell'], leftIndent=13, firstLineIndent=-13, **gap)
            items += [(f'{i}. {x}', st, None) for i, x in enumerate(b['numbered'], 1)]
        else:
            items.append((b, ParagraphStyle('p', parent=base, **gap), None))
    out = []
    for k, (text, st, bullet) in enumerate(items):
        if k == len(items) - 1:
            st = ParagraphStyle('last', parent=st, spaceAfter=0)
        out.append(Paragraph(rich(text), st, bulletText=bullet) if bullet else Paragraph(rich(text), st))
    return out


def make_table(tbl):
    cols = tbl['columns']; numbered = tbl.get('numbered', False)
    names = ([tbl.get('num_header', '#')] if numbered else []) + [c['name'] for c in cols]
    num_w = tbl.get('num_width', 25)
    ratios = [c['width'] for c in cols]
    avail = TABLE_W - (num_w if numbered else 0)
    widths = ([num_w] if numbered else []) + [avail * r / sum(ratios) for r in ratios]
    bold_cols = {i + (1 if numbered else 0) for i, c in enumerate(cols) if c.get('bold')}
    data = [[cell_flowables(n, header=True) for n in names]]
    for i, row in enumerate(tbl['rows'], 1):
        if len(row) != len(cols):
            sys.exit(f"table '{tbl.get('title', '')}' row {i} has {len(row)} cells, expected {len(cols)}")
        cells = ([cell_flowables(str(i))] if numbered else [])
        cells += [cell_flowables(v, bold=(j + (1 if numbered else 0)) in bold_cols) for j, v in enumerate(row)]
        data.append(cells)
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    style = [('BACKGROUND', (0, 0), (-1, 0), NAVY), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
             ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
             ('TOPPADDING', (0, 0), (-1, -1), 6.3), ('BOTTOMPADDING', (0, 0), (-1, -1), 6.7),
             ('TOPPADDING', (0, 0), (-1, 0), 5), ('BOTTOMPADDING', (0, 0), (-1, 0), 5.5),
             ('LINEBELOW', (0, 0), (-1, -1), 0.5, RULE), ('LINEABOVE', (0, 0), (-1, 0), 0.5, RULE)]
    for r in range(2, len(data), 2):
        style.append(('BACKGROUND', (0, r), (-1, r), STRIPE))
    t.setStyle(TableStyle(style))
    return t


def paras(items):
    return [Paragraph(rich(x), ST['body']) for x in (items if isinstance(items, list) else [items])]


class Doc(BaseDocTemplate):
    def __init__(self, path, spec, pages=None):
        super().__init__(path, pagesize=(W, H), leftMargin=LM, rightMargin=W - RM_X, topMargin=72, bottomMargin=792 - 722,
                         title=f"Scope of Work — {spec['cover']['client']}", author=spec['cover'].get('prepared_by', 'CallKaro AI'))
        self.spec = spec; self.pages = pages or {}; self.found = {}; self.total_pages = None
        fr = Frame(LM, 792 - 722, RM_X - LM, 722 - 72, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id='main', frames=[fr], onPage=self.decor)])

    def decor(self, c, doc):
        cv = self.spec['cover']
        c.saveState()
        c.drawImage(LOGO, 459.5, H - 35.35 - 16.5, 16.5, 16.5, mask='auto')
        c.setFont('Carlito-Bold', 10.5); c.setFillColor(NAVY); c.drawString(480, H - 47.2, 'CallKaro AI')
        c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(LM, H - 738, RM_X, H - 738)
        foot = cv.get('footer') or f"Scope of Work · {cv['client']} · Prepared by {cv.get('prepared_by', 'CallKaro AI')} · {cv.get('classification', 'Confidential')}"
        c.setFont('Carlito-Regular', 8); c.setFillColor(GREY); c.drawString(LM, H - 754.3, foot)
        total = self.pages.get('_total', '?'); n = str(doc.page)
        parts = [('Page ', 9, GREY), (n, 11, TXT), (' of ', 9, GREY), (str(total), 11, TXT)]
        x = 519 - sum(pdfmetrics.stringWidth(t, 'Carlito-Regular', s) for t, s, _ in parts)
        for t, s, col in parts:
            c.setFont('Carlito-Regular', s); c.setFillColor(col); c.drawString(x, H - 755.3, t)
            x += pdfmetrics.stringWidth(t, 'Carlito-Regular', s)
        c.restoreState()

    def afterFlowable(self, fl):
        if isinstance(fl, Heading) and fl.key:
            self.found[fl.key] = self.page


class Cover(Flowable):
    def __init__(self, cv):
        super().__init__(); self.cv = cv

    def wrap(self, aw, ah):
        return aw, 600

    def draw(self):
        c = self.canv; cv = self.cv; cx = (RM_X - LM) / 2
        top = 70  # frame top in page coords from top; y = H - page_y, relative to frame bottom
        def y(pt_from_top): return (H - pt_from_top) - (H - 72 - 600)
        def line(ty):
            c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(cx - 12.5, y(ty), cx + 12.5, y(ty))
        def text(ty, s, font, size, col):
            while size > 9 and pdfmetrics.stringWidth(s, font, size) > (RM_X - LM) - 10:
                size -= 1   # shrink long client / subtitle lines to fit the page
            c.setFont(font, size); c.setFillColor(col); c.drawCentredString(cx, y(ty) - size * 0.33, s)
        line(220.5)
        text(242, 'SCOPE OF WORK', 'Carlito-Bold', 11, TXT)
        text(279, cv['client'], 'Carlito-Bold', 36, BLUE)
        text(317, cv['subtitle'], 'Carlito-Italic', 13, TXT)
        line(346.5)
        text(383, 'Prepared by', 'Carlito-Italic', 11, TXT)
        text(401, cv.get('prepared_by', 'CallKaro AI'), 'Carlito-Bold', 13, TXT)
        text(440, cv.get('confidential_line') or f"Confidential — For {cv['client']} Use Only", 'Carlito-Italic', 10, GREY)
        text(456, cv['date'], 'Carlito-Regular', 10, GREY)
        text(470, f"Version {cv.get('version', '1.0')}", 'Carlito-Regular', 9, GREY)


def story(spec, pages):
    cv = spec['cover']; s = []
    s += [Cover(cv), PageBreak()]
    entries = [('Purpose of this Document', 'purpose')] + [(sec['title'], f'sec{i}') for i, sec in enumerate(spec['sections'], 1)]
    s += [Heading('Table of Contents')]
    s += [TocLine(t, pages.get(k, '?')) for t, k in entries]
    s += [PageBreak(), Heading('Purpose of this Document', key='purpose')]
    pu = spec['purpose']
    s += paras(pu['text'])
    details = pu.get('details') or [['Client', cv['client']], ['Prepared by', cv.get('prepared_by', 'CallKaro AI')], ['Date', cv['date']]]
    s += [Spacer(1, 5), make_table({'columns': [{'name': 'Field', 'width': 120, 'bold': True}, {'name': 'Detail', 'width': 350}], 'rows': details})]
    for i, sec in enumerate(spec['sections'], 1):
        s += [PageBreak(), Heading(sec['title'], key=f'sec{i}')]
        s += paras(sec.get('intro', []))
        for blk in sec.get('tables', [sec] if 'columns' in sec else []):
            if blk.get('caption'): s += [Spacer(1, 8)] + paras(blk['caption'])
            s += [Spacer(1, 5), make_table(blk)]
        s += paras(sec.get('outro', []))
    return s


def build(spec, out):
    fonts()
    pages = {}
    for _ in range(3):  # pass 1 finds page numbers, later passes settle TOC + "of N"
        d = Doc(out, spec, pages)
        d.build(story(spec, pages))
        found = dict(d.found); found['_total'] = d.page
        if found == pages: break
        pages = found
    return pages


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('--out')
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding='utf-8'))
    for k in ('client', 'subtitle', 'date'):
        if not spec.get('cover', {}).get(k): sys.exit(f"spec.cover.{k} is required")
    if not spec.get('purpose', {}).get('text'): sys.exit('spec.purpose.text is required')
    if not spec.get('sections'): sys.exit('spec.sections is empty')
    out = a.out or re.sub(r'[^A-Za-z0-9]+', '_', spec['cover']['client']).strip('_') + '_SoW.pdf'
    pages = build(spec, out)
    print('saved', out, 'pages:', pages['_total'])


if __name__ == '__main__':
    main()
