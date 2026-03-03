#!/usr/bin/env python3
"""Generate a PDF document from the TP React Native documentation."""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, Image, KeepTogether
)
from PIL import Image as PILImage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
IMG_DIR = os.path.join(DOCS_DIR, "img")
OUTPUT_PDF = os.path.join(BASE_DIR, "tp-react-native.pdf")

# Colors
PRIMARY = HexColor("#007AFF")
DARK = HexColor("#1a1a2e")
LIGHT_BG = HexColor("#f8f9fa")
TIP_BG = HexColor("#e8f5e9")
TIP_BORDER = HexColor("#4caf50")
INFO_BG = HexColor("#e3f2fd")
INFO_BORDER = HexColor("#2196f3")
TASK_BG = HexColor("#fff3e0")
TASK_BORDER = HexColor("#ff9800")
DANGER_BG = HexColor("#ffebee")
DANGER_BORDER = HexColor("#f44336")


def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'DocTitle', parent=styles['Title'],
        fontSize=26, textColor=white, alignment=TA_CENTER,
        spaceAfter=8, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=16, textColor=PRIMARY, spaceBefore=14, spaceAfter=6,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=12, textColor=DARK, spaceBefore=12, spaceAfter=4,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'H3', parent=styles['Heading3'],
        fontSize=10, textColor=HexColor("#333333"), spaceBefore=8, spaceAfter=3,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'H4', parent=styles['Heading3'],
        fontSize=9, textColor=HexColor("#444444"), spaceBefore=6, spaceAfter=2,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=9, leading=12, spaceAfter=4,
        fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'CodeBlock', parent=styles['Normal'],
        fontSize=7, leading=9, fontName='Courier',
        backColor=HexColor("#f4f4f4"), textColor=HexColor("#333333"),
        leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=4,
        borderWidth=0.5, borderColor=HexColor("#dddddd"), borderPadding=6,
        borderRadius=2
    ))
    styles.add(ParagraphStyle(
        'CodeInAdmonition', parent=styles['Normal'],
        fontSize=6.5, leading=8.5, fontName='Courier',
        backColor=HexColor("#eeeeee"), textColor=HexColor("#333333"),
        leftIndent=6, rightIndent=6, spaceBefore=3, spaceAfter=3,
        borderWidth=0.5, borderColor=HexColor("#cccccc"), borderPadding=5
    ))
    for name, bg, border in [
        ('TipBox', TIP_BG, TIP_BORDER),
        ('InfoBox', INFO_BG, INFO_BORDER),
        ('TaskBox', TASK_BG, TASK_BORDER),
        ('DangerBox', DANGER_BG, DANGER_BORDER),
    ]:
        styles.add(ParagraphStyle(
            name, parent=styles['Normal'],
            fontSize=8, leading=11, fontName='Helvetica',
            backColor=bg, leftIndent=8, rightIndent=8,
            spaceBefore=4, spaceAfter=4, borderWidth=1,
            borderColor=border, borderPadding=6
        ))
    styles.add(ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontSize=8, leading=10, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontSize=8, leading=10, fontName='Helvetica-Bold', textColor=white
    ))
    return styles


def escape_xml(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def process_inline(text):
    """Convert markdown inline formatting to reportlab XML. Input should already be XML-escaped."""
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" size="7" color="#c7254e">\1</font>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<font color="#007AFF"><u>\1</u></font>', text)
    return text


def collect_admonition_raw(lines, start_idx):
    """Collect all raw lines belonging to an admonition starting at start_idx.
    Returns (admonition_type, title, raw_content_lines, next_idx)."""
    match = re.match(r'^(\s*)!!! (\w+)(?:\s+"([^"]*)")?', lines[start_idx])
    if not match:
        return None, None, [], start_idx + 1
    base_indent = len(match.group(1))
    adm_type = match.group(2)
    title = match.group(3)
    content_indent = base_indent + 4
    idx = start_idx + 1
    raw_lines = []
    while idx < len(lines):
        line = lines[idx]
        if line.strip() == '':
            raw_lines.append('')
            idx += 1
            continue
        # Check if line has enough indent to belong to this admonition
        stripped = line.lstrip()
        current_indent = len(line) - len(stripped)
        if current_indent >= content_indent:
            raw_lines.append(line[content_indent:])
            idx += 1
        else:
            break
    return adm_type, title, raw_lines, idx


def render_admonition_content(raw_lines, styles):
    """Parse admonition content which may contain code blocks, nested admonitions, and text."""
    flowables = []
    i = 0
    text_buffer = []

    def flush_text():
        nonlocal text_buffer
        if text_buffer:
            content = '\n'.join(text_buffer).strip()
            if content:
                processed = process_inline(escape_xml(content))
                processed = processed.replace('\n', '<br/>')
                flowables.append(Paragraph(processed, styles['Body']))
            text_buffer = []

    while i < len(raw_lines):
        line = raw_lines[i]

        # Nested admonition
        nested_match = re.match(r'^!!! (\w+)(?:\s+"([^"]*)")?', line)
        if nested_match:
            flush_text()
            # Collect nested admonition
            nested_type, nested_title, nested_lines, next_i = collect_admonition_raw(raw_lines, i)
            nested_flowables = render_admonition_flowables(nested_type, nested_title, nested_lines, styles)
            flowables.extend(nested_flowables)
            i = next_i
            continue

        # Code block
        if line.strip().startswith('```'):
            flush_text()
            code_lines = []
            i += 1
            while i < len(raw_lines) and not raw_lines[i].strip().startswith('```'):
                code_lines.append(raw_lines[i])
                i += 1
            if i < len(raw_lines):
                i += 1  # skip closing ```
            code_text = escape_xml('\n'.join(code_lines))
            if code_text.strip():
                flowables.append(Paragraph(
                    code_text.replace('\n', '<br/>'),
                    styles['CodeInAdmonition']
                ))
            continue

        text_buffer.append(line)
        i += 1

    flush_text()
    return flowables


def render_admonition_flowables(adm_type, title, raw_lines, styles):
    """Render a complete admonition as a colored table wrapping its content."""
    type_map = {
        'tip': (TIP_BG, TIP_BORDER, 'Conseil'),
        'info': (INFO_BG, INFO_BORDER, 'Info'),
        'example': (TASK_BG, TASK_BORDER, 'Exercice'),
        'danger': (DANGER_BG, DANGER_BORDER, 'Important'),
        'warning': (DANGER_BG, DANGER_BORDER, 'Attention'),
    }
    bg, border, default_label = type_map.get(adm_type, (INFO_BG, INFO_BORDER, adm_type.capitalize()))
    label = title if title else default_label

    inner_flowables = []
    # Label
    inner_flowables.append(Paragraph(
        f'<b>{escape_xml(label)}</b>',
        ParagraphStyle('AdmLabel', parent=styles['Body'], fontSize=8, fontName='Helvetica-Bold',
                       spaceAfter=2, spaceBefore=0)
    ))
    # Content
    content_flowables = render_admonition_content(raw_lines, styles)
    inner_flowables.extend(content_flowables)

    if not content_flowables and not label:
        return []

    # Wrap in a colored table for the box effect
    available_width = A4[0] - 4 * cm
    t = Table([[inner_flowables]], colWidths=[available_width - 8 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('BOX', (0, 0), (-1, -1), 1.5, border),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return [Spacer(1, 3), t, Spacer(1, 3)]


def parse_markdown(md_content, styles):
    """Parse markdown content and return a list of reportlab flowables."""
    flowables = []
    lines = md_content.split('\n')
    i = 0
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]

        # Code blocks (top-level)
        if line.strip().startswith('```') and not in_code_block:
            in_code_block = True
            code_lines = []
            i += 1
            continue

        if in_code_block:
            if line.strip().startswith('```'):
                code_text = escape_xml('\n'.join(code_lines))
                if code_text.strip():
                    flowables.append(Paragraph(
                        code_text.replace('\n', '<br/>'),
                        styles['CodeBlock']
                    ))
                in_code_block = False
                code_lines = []
            else:
                code_lines.append(line)
            i += 1
            continue

        # Admonitions
        if re.match(r'^!!! \w+', line):
            adm_type, title, raw_lines, next_i = collect_admonition_raw(lines, i)
            flowables.extend(render_admonition_flowables(adm_type, title, raw_lines, styles))
            i = next_i
            continue

        # Empty line
        if not line.strip():
            i += 1
            continue

        # H1
        if line.startswith('# ') and not line.startswith('## '):
            text = process_inline(escape_xml(line[2:].strip()))
            flowables.append(Paragraph(text, styles['H1']))
            flowables.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=0, spaceAfter=6))
            i += 1
            continue

        # H2
        if line.startswith('## '):
            text = process_inline(escape_xml(line[3:].strip()))
            flowables.append(Paragraph(text, styles['H2']))
            i += 1
            continue

        # H3
        if line.startswith('### '):
            text = process_inline(escape_xml(line[4:].strip()))
            flowables.append(Paragraph(text, styles['H3']))
            i += 1
            continue

        # H4
        if line.startswith('#### '):
            text = process_inline(escape_xml(line[5:].strip()))
            flowables.append(Paragraph(text, styles['H4']))
            i += 1
            continue

        # Tables
        if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            flowables.extend(render_table(table_lines, styles))
            continue

        # Images (possibly multiple on one line or consecutive)
        img_match = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
        if img_match:
            # Collect all images on this line
            imgs_on_line = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
            img_flowables = []
            for alt_text, img_path in imgs_on_line:
                img_path = img_path.split('{')[0].strip()
                if img_path.startswith('../img/'):
                    img_path = os.path.join(IMG_DIR, img_path.replace('../img/', ''))
                elif img_path.startswith('img/'):
                    img_path = os.path.join(IMG_DIR, img_path.replace('img/', ''))
                if os.path.exists(img_path):
                    try:
                        pil_img = PILImage.open(img_path)
                        iw, ih = pil_img.size
                        max_w = 120
                        ratio = max_w / iw
                        dw, dh = max_w, ih * ratio
                        if dh > 250:
                            dh = 250
                            dw = iw * (250 / ih)
                        img = Image(img_path, width=dw, height=dh)
                        img_flowables.append(img)
                    except Exception:
                        pass

            if len(img_flowables) > 1:
                # Side by side in a table
                t = Table([img_flowables], colWidths=[(A4[0] - 4 * cm) / len(img_flowables)] * len(img_flowables))
                t.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                flowables.append(Spacer(1, 4))
                flowables.append(t)
                flowables.append(Spacer(1, 4))
            elif img_flowables:
                img_flowables[0].hAlign = 'CENTER'
                flowables.append(Spacer(1, 4))
                flowables.append(img_flowables[0])
                flowables.append(Spacer(1, 4))
            i += 1
            continue

        # List items
        list_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.+)', line)
        if list_match:
            indent = len(list_match.group(1))
            marker = list_match.group(2)
            content = list_match.group(3)
            content = process_inline(escape_xml(content))
            bullet = '\u2022' if marker in ['-', '*'] else marker
            left_indent = 15 + indent * 8
            flowables.append(Paragraph(
                f"{bullet}  {content}",
                ParagraphStyle('ListItem', parent=styles['Body'],
                               leftIndent=left_indent, firstLineIndent=0, spaceAfter=2)
            ))
            i += 1
            continue

        # Regular paragraph
        text = process_inline(escape_xml(line.strip()))
        if text:
            flowables.append(Paragraph(text, styles['Body']))
        i += 1

    return flowables


def render_table(table_lines, styles):
    flowables = []
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if all(re.match(r'^[-:]+$', c) for c in cells):
            continue
        rows.append(cells)
    if not rows:
        return flowables

    table_data = []
    for row_idx, row in enumerate(rows):
        table_row = []
        for cell in row:
            cell_text = process_inline(escape_xml(cell))
            style = styles['TableHeader'] if row_idx == 0 else styles['TableCell']
            table_row.append(Paragraph(cell_text, style))
        table_data.append(table_row)

    available_width = A4[0] - 4 * cm
    num_cols = len(table_data[0])
    col_width = available_width / num_cols

    table = Table(table_data, colWidths=[col_width] * num_cols)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
        ('ROUNDEDCORNERS', [3, 3, 3, 3]),
    ]))
    flowables.append(Spacer(1, 4))
    flowables.append(table)
    flowables.append(Spacer(1, 4))
    return flowables


def add_cover_page(flowables, styles):
    flowables.append(Spacer(1, 6 * cm))

    title_data = [[Paragraph("TP React Native", styles['DocTitle'])]]
    title_table = Table(title_data, colWidths=[14 * cm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 18),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    flowables.append(title_table)
    flowables.append(Spacer(1, 0.8 * cm))

    flowables.append(Paragraph(
        "Applications mobiles avec React Native et Expo",
        ParagraphStyle('CoverSub', parent=styles['Normal'],
                       fontSize=12, textColor=HexColor("#666666"), alignment=TA_CENTER)
    ))
    flowables.append(Spacer(1, 0.3 * cm))
    flowables.append(Paragraph(
        "UMONS - Informatique de Gestion",
        ParagraphStyle('CoverInfo', parent=styles['Normal'],
                       fontSize=10, textColor=HexColor("#999999"), alignment=TA_CENTER)
    ))
    flowables.append(Spacer(1, 2 * cm))

    flowables.append(Paragraph("Table des matieres",
        ParagraphStyle('TOCTitle', parent=styles['H2'], alignment=TA_CENTER)))
    flowables.append(Spacer(1, 0.4 * cm))

    toc_items = [
        "0.  Prerequis",
        "1.  Exercice 0 : Creer un projet",
        "2.  Exercice 1 : Hello World (Counter)",
        "3.  Exercice 2 : DevNotes",
        "4.  Exercice 3 : DevHub",
    ]
    for item in toc_items:
        flowables.append(Paragraph(item,
            ParagraphStyle('TOCItem', parent=styles['Body'],
                           fontSize=10, alignment=TA_CENTER, spaceAfter=3)))
    flowables.append(PageBreak())


def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    if page_num > 1:
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(HexColor("#999999"))
        canvas.drawCentredString(A4[0] / 2, 1.2 * cm, f"Page {page_num - 1}")
        canvas.setStrokeColor(PRIMARY)
        canvas.setLineWidth(0.3)
        canvas.line(2 * cm, A4[1] - 1.5 * cm, A4[0] - 2 * cm, A4[1] - 1.5 * cm)
        canvas.setFont('Helvetica', 6)
        canvas.setFillColor(HexColor("#bbbbbb"))
        canvas.drawString(2 * cm, A4[1] - 1.3 * cm, "TP React Native - UMONS")
        canvas.restoreState()


def main():
    styles = get_styles()
    doc = SimpleDocTemplate(
        OUTPUT_PDF, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm,
    )
    flowables = []
    add_cover_page(flowables, styles)

    sections = [
        "docs/index.md",
        "docs/prerequisites.md",
        "docs/exercices/00-create-project.md",
        "docs/exercices/01-hello-world.md",
        "docs/exercices/02-devnotes.md",
        "docs/exercices/03-devhub.md",
    ]

    for idx, filepath in enumerate(sections):
        full_path = os.path.join(BASE_DIR, filepath)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        flowables.extend(parse_markdown(content, styles))
        if idx < len(sections) - 1:
            flowables.append(PageBreak())

    doc.build(flowables, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
