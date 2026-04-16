"""Markdown -> PDF using reportlab. Handles headings, paragraphs, tables,
inline bold/italic/code, bullet lists. Academic-style A4, 11pt body."""
import re
import sys
from pathlib import Path
import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from html.parser import HTMLParser

if len(sys.argv) != 3:
    sys.exit("usage: md_to_pdf.py <input.md> <output.pdf>")
src = Path(sys.argv[1]); dst = Path(sys.argv[2])
md_text = src.read_text(encoding="utf-8")

# Convert markdown to HTML
html = markdown2.markdown(md_text, extras=["tables", "fenced-code-blocks",
                                            "strike", "target-blank-links",
                                            "break-on-newline"])

# Strip emoji and problematic unicode (replace with ASCII approximations)
REPLACEMENTS = {
    "\u2014": "--", "\u2013": "-", "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00a0": " ",
    "\u00b7": "*", "\u2022": "*", "\u2265": ">=", "\u2264": "<=",
    "\u00d7": "x", "\u00b1": "+/-", "\u00b2": "^2", "\u00b3": "^3",
    "\u03b1": "alpha", "\u03c7": "chi", "\u03c3": "sigma", "\u03bc": "mu",
    "\u2192": "->", "\u2190": "<-", "\u2261": "==",
    "\u00e9": "e", "\u00e8": "e", "\u00ea": "e",
    "\u00ff": "y", "\u00e1": "a", "\u00e0": "a", "\u00e4": "a",
    "\u00ed": "i", "\u00ee": "i", "\u00fc": "u", "\u00f6": "o",
    "\u010d": "c", "\u0161": "s", "\u017e": "z",
    "\u2070": "0", "\u2074": "4",
    "\u221e": "infinity",
}
def clean(s):
    for k, v in REPLACEMENTS.items():
        s = s.replace(k, v)
    return s

# Styles
styles = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=styles["BodyText"],
                      fontName="Helvetica", fontSize=10.5, leading=14,
                      alignment=TA_JUSTIFY, spaceBefore=2, spaceAfter=4)
H1 = ParagraphStyle("h1", parent=styles["Heading1"],
                    fontName="Helvetica-Bold", fontSize=18, leading=22,
                    spaceBefore=12, spaceAfter=8)
H2 = ParagraphStyle("h2", parent=styles["Heading2"],
                    fontName="Helvetica-Bold", fontSize=14, leading=18,
                    spaceBefore=12, spaceAfter=6)
H3 = ParagraphStyle("h3", parent=styles["Heading3"],
                    fontName="Helvetica-Bold", fontSize=12, leading=16,
                    spaceBefore=8, spaceAfter=4)
CODE = ParagraphStyle("code", parent=BODY, fontName="Courier",
                      fontSize=9, leading=11)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=20,
                        bulletIndent=8, spaceBefore=1, spaceAfter=1)

TABLE_STYLE = TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6e6e6")),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
])

# Parse HTML into flowables
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.flowables = []
        self.buf = []
        self.stack = []       # tag stack
        self.in_code_block = False
        self.table = None     # current table: list of rows
        self.current_row = None
        self.current_cell = []
        self.list_stack = []  # for nested lists
        self.inline_buf = ""

    def text_handle(self, data):
        if not self.stack: return
        top = self.stack[-1]
        if top in ("pre",):
            self.buf.append(clean(data))
        else:
            # decorate based on nearest inline tags
            s = clean(data)
            # apply inline decorations
            inline_stack = [t for t in self.stack
                            if t in ("strong", "em", "code", "b", "i")]
            for t in reversed(inline_stack):
                if t in ("strong", "b"):
                    s = f"<b>{s}</b>"
                elif t in ("em", "i"):
                    s = f"<i>{s}</i>"
                elif t == "code":
                    s = f"<font name='Courier' size='9'>{s}</font>"
            self.inline_buf += s

    def flush_paragraph(self, style=BODY):
        txt = self.inline_buf.strip()
        self.inline_buf = ""
        if txt:
            txt = txt.replace("\n", " ")
            self.flowables.append(Paragraph(txt, style))

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        if tag in ("h1","h2","h3","p","li"):
            self.flush_paragraph()
        elif tag == "table":
            self.table = []
        elif tag == "tr":
            self.current_row = []
        elif tag in ("td","th"):
            self.inline_buf = ""
        elif tag in ("ul","ol"):
            self.list_stack.append(tag)
        elif tag == "hr":
            self.flush_paragraph()
            self.flowables.append(Spacer(1, 6))
            self.flowables.append(
                Table([[""]], colWidths=[16*cm], rowHeights=[1],
                      style=TableStyle([("LINEABOVE", (0,0),(-1,0),
                                         0.5, colors.grey)])))
            self.flowables.append(Spacer(1, 6))

    def handle_endtag(self, tag):
        if tag == "h1":
            self.flush_paragraph(H1)
        elif tag == "h2":
            self.flush_paragraph(H2)
        elif tag == "h3":
            self.flush_paragraph(H3)
        elif tag == "p":
            self.flush_paragraph(BODY)
        elif tag == "li":
            # bullet prefix
            if self.list_stack and self.list_stack[-1] == "ol":
                # simple numbering fallback: use bullet '*'
                prefix = "&bull; "
            else:
                prefix = "&bull; "
            txt = self.inline_buf.strip()
            self.inline_buf = ""
            if txt:
                self.flowables.append(Paragraph(prefix + txt, BULLET))
        elif tag in ("ul","ol"):
            if self.list_stack: self.list_stack.pop()
            self.flowables.append(Spacer(1, 4))
        elif tag in ("td","th"):
            self.current_row.append(self.inline_buf.strip())
            self.inline_buf = ""
        elif tag == "tr":
            if self.current_row is not None and self.table is not None:
                self.table.append(self.current_row)
            self.current_row = None
        elif tag == "table":
            if self.table and len(self.table) > 1:
                # Render table
                data = []
                for row in self.table:
                    data.append([Paragraph(cell or " ", BODY) for cell in row])
                # Compute column widths proportionally
                ncols = max(len(r) for r in self.table)
                col_w = (16.5*cm) / ncols
                t = Table(data, colWidths=[col_w]*ncols, repeatRows=1)
                t.setStyle(TABLE_STYLE)
                self.flowables.append(Spacer(1, 4))
                self.flowables.append(t)
                self.flowables.append(Spacer(1, 6))
            self.table = None
        # pop from stack
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data):
        self.text_handle(data)

p = Parser()
p.feed(html)
p.flush_paragraph()

# Build doc
doc = SimpleDocTemplate(
    str(dst), pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="A Scribe-Specific Vowel-Pattern Classifier for the Voynich Manuscript",
    author="Ben Horne / Brain-V")
doc.build(p.flowables)
print(f"Wrote: {dst}")
print(f"Size: {dst.stat().st_size} bytes")
