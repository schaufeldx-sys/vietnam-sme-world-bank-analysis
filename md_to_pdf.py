"""
Convert capstone_case_study.md -> capstone_case_study.pdf
Pure-Python: mistune AST (v3) -> reportlab Platypus.
"""
import os
import re
import mistune
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Preformatted, KeepTogether,
)

ROOT = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(ROOT, "capstone_case_study.md")
PDF_PATH = os.path.join(ROOT, "capstone_case_study.pdf")

# ---------- Inline renderer ----------
def escape(s):
    return (str(s).replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;"))

def render_inline(tokens):
    """Convert mistune inline token list to reportlab inline markup."""
    out = []
    for tok in tokens or []:
        t = tok.get("type")
        if t == "text":
            out.append(escape(tok.get("raw", "")))
        elif t == "codespan":
            out.append(f'<font color="#c7254e" face="Courier">'
                       f'{escape(tok.get("raw", ""))}</font>')
        elif t == "strong":
            out.append("<b>" + render_inline(tok.get("children", [])) + "</b>")
        elif t == "emphasis":
            out.append("<i>" + render_inline(tok.get("children", [])) + "</i>")
        elif t == "link":
            inner = render_inline(tok.get("children", []))
            out.append(f'<font color="#3182ce"><u>{inner}</u></font>')
        elif t == "softbreak":
            out.append(" ")
        elif t == "linebreak":
            out.append("<br/>")
        elif t == "image":
            alt = escape(tok.get("alt", ""))
            out.append(f'<i>[image: {alt}]</i>')
        elif t == "inline_html":
            # strip stray raw HTML
            raw = tok.get("raw", "")
            out.append(escape(raw))
        else:
            out.append(escape(str(tok.get("raw", ""))))
    return "".join(out)

# ---------- Styles ----------
styles = getSampleStyleSheet()
TITLE = ParagraphStyle("title", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=20, leading=24,
    textColor=colors.HexColor("#1a365d"), spaceAfter=10)
SUBTITLE = ParagraphStyle("subtitle", parent=styles["Normal"],
    fontName="Helvetica-Oblique", fontSize=11, leading=14,
    textColor=colors.HexColor("#4a5568"), spaceAfter=12)
H1 = ParagraphStyle("h1", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=15, leading=18,
    textColor=colors.HexColor("#1a365d"),
    spaceBefore=14, spaceAfter=8)
H2 = ParagraphStyle("h2", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=13, leading=16,
    textColor=colors.HexColor("#1a365d"),
    spaceBefore=12, spaceAfter=6)
H3 = ParagraphStyle("h3", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=11.5, leading=14,
    textColor=colors.HexColor("#2c5282"),
    spaceBefore=10, spaceAfter=5)
P = ParagraphStyle("p", parent=styles["Normal"],
    fontName="Helvetica", fontSize=10, leading=13.5,
    spaceAfter=5, textColor=colors.HexColor("#1a202c"))
BQ = ParagraphStyle("bq", parent=styles["Normal"],
    fontName="Helvetica-Oblique", fontSize=10, leading=14,
    leftIndent=12, rightIndent=6,
    backColor=colors.HexColor("#ebf8ff"),
    borderColor=colors.HexColor("#3182ce"),
    textColor=colors.HexColor("#2c5282"),
    borderPadding=6, spaceBefore=6, spaceAfter=8)
CODE = ParagraphStyle("code", parent=styles["Normal"],
    fontName="Courier", fontSize=8.5, leading=11,
    backColor=colors.HexColor("#2d3748"),
    textColor=colors.HexColor("#f7fafc"),
    leftIndent=2, rightIndent=2,
    borderPadding=6, spaceBefore=4, spaceAfter=4)
LI = ParagraphStyle("li", parent=styles["Normal"],
    fontName="Helvetica", fontSize=10, leading=13.5,
    leftIndent=16, bulletIndent=4, spaceAfter=2)

# ---------- Block walker ----------
def render_blocks(tokens, story):
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        t = tok.get("type")

        if t == "blank_line":
            i += 1
            continue

        elif t == "heading":
            level = tok["attrs"]["level"]
            text = render_inline(tok.get("children", []))
            style = {1: H1, 2: H2}.get(level, H3)
            if text.strip():
                story.append(Paragraph(text, style))
            i += 1

        elif t == "paragraph":
            text = render_inline(tok.get("children", [])).strip()
            if text:
                story.append(Paragraph(text, P))
            i += 1

        elif t in ("blockquote", "block_quote"):
            # Render blockquote contents as indented paragraphs
            for child in tok.get("children", []):
                if child.get("type") == "paragraph":
                    text = render_inline(child.get("children", [])).strip()
                    if text:
                        story.append(Paragraph(text, BQ))
                else:
                    # recurse for nested content
                    inner = []
                    render_blocks([child], inner)
                    story.extend(inner)
            i += 1

        elif t == "block_code":
            lang = (tok.get("attrs", {}) or {}).get("info", "")
            raw = tok.get("raw", "").rstrip("\n")
            for line in raw.split("\n"):
                story.append(Preformatted(line if line else " ", CODE))
            story.append(Spacer(1, 0.2*cm))
            i += 1

        elif t == "list":
            ordered = (tok.get("attrs", {}) or {}).get("ordered", False)
            items = tok.get("children", [])
            for j, item in enumerate(items, 1):
                inline_text = collect_paragraph_text(item.get("children", []))
                bullet = f"{j}." if ordered else "\u2022"
                story.append(Paragraph(inline_text, LI, bulletText=bullet))
            story.append(Spacer(1, 0.15*cm))
            i += 1

        elif t == "thematic_break":
            story.append(Spacer(1, 0.3*cm))
            i += 1

        elif t == "table":
            story.append(render_table(tok))
            story.append(Spacer(1, 0.3*cm))
            i += 1

        else:
            # Unknown / fallback
            raw = tok.get("raw", "")
            if raw.strip():
                story.append(Paragraph(escape(raw)[:200], P))
            i += 1

def collect_paragraph_text(tokens):
    """Join inline text from a list item's children.
    Children may include block_text wrappers around paragraphs, or
    inline tokens directly. Walk down to find any paragraph or text."""
    out = []
    for tok in tokens or []:
        tt = tok.get("type")
        if tt == "paragraph":
            out.append(render_inline(tok.get("children", [])))
        elif tt == "block_text":
            # nested block wrapper
            out.append(render_inline(tok.get("children", [])))
        elif tt == "text":
            out.append(escape(tok.get("raw", "")))
        elif tt in ("strong", "emphasis"):
            out.append(render_inline(tok.get("children", [])))
        elif tt == "list":
            # nested sublist - skip for inline text
            pass
    return "".join(out).strip()

def render_table(tok):
    """Render a mistune table token into a reportlab Table."""
    rows = []
    # Head
    head = tok.get("children", [])
    if head and head[0].get("type") == "table_head":
        head_row = []
        for cell in head[0].get("children", []):
            text = render_inline(cell.get("children", [])).strip()
            head_row.append(text)
        rows.append(head_row)
    # Body
    body = head[1] if len(head) > 1 else None
    if body and body.get("type") == "table_body":
        for row in body.get("children", []):
            data_row = []
            for cell in row.get("children", []):
                text = render_inline(cell.get("children", [])).strip()
                data_row.append(text)
            rows.append(data_row)

    if not rows:
        return Spacer(1, 0.1*cm)

    n_cols = max(len(r) for r in rows)
    for r in rows:
        while len(r) < n_cols:
            r.append("")

    # Convert inline markup (font tags etc.) to Paragraphs so reportlab
    # parses them properly inside cells.
    rows_as_paras = []
    for r_idx, r in enumerate(rows):
        is_header = (r_idx == 0)
        style = ParagraphStyle(
            "cell" + str(r_idx),
            fontName="Helvetica-Bold" if is_header else "Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1a202c"),
        )
        row_paras = [Paragraph(c if c else "&nbsp;", style) for c in r]
        rows_as_paras.append(row_paras)

    tbl = Table(rows_as_paras, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#edf2f7")),
        ("GRID",       (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e0")),
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("RIGHTPADDING",  (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS",(0,1), (-1,-1),
            [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    return tbl

# ---------- Main ----------
def md_to_pdf(md_file, pdf_file):
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Strip the leading H1 (we render it as title with subtitle)
    md_text = re.sub(r"^# [^\n]*\n", "", md_text, count=1)

    md = mistune.create_markdown(renderer=None, plugins=["table"])
    tokens = md(md_text)

    doc = SimpleDocTemplate(pdf_file, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm,
                            title="Vietnam SME Banking Access Capstone")

    story = []
    story.append(Paragraph(
        "Vietnam SME Banking Access: A Data-Driven Analysis", TITLE))
    story.append(Paragraph(
        "<i>Google Data Analytics Capstone Project — Final Deliverable</i>",
        SUBTITLE))
    story.append(Spacer(1, 0.3*cm))

    render_blocks(tokens, story)

    doc.build(story)
    print(f"PDF written: {pdf_file}  ({os.path.getsize(pdf_file):,} bytes)")

if __name__ == "__main__":
    md_to_pdf(MD_PATH, PDF_PATH)
