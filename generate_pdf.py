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
    Preformatted, KeepTogether, HRFlowable, Image
)
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
IMG_DIR = os.path.join(DOCS_DIR, "img")
OUTPUT_PDF = os.path.join(BASE_DIR, "tp-react-native.pdf")

# Colors
PRIMARY = HexColor("#007AFF")
DARK = HexColor("#1a1a2e")
LIGHT_BG = HexColor("#f8f9fa")
CODE_BG = HexColor("#2d2d2d")
CODE_TEXT = HexColor("#f8f8f2")
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
        fontSize=28, textColor=white, alignment=TA_CENTER,
        spaceAfter=10, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontSize=14, textColor=HexColor("#cccccc"), alignment=TA_CENTER,
        spaceAfter=20, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=22, textColor=PRIMARY, spaceBefore=20, spaceAfter=12,
        fontName='Helvetica-Bold', borderWidth=0,
        borderPadding=0, borderColor=PRIMARY
    ))
    styles.add(ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=16, textColor=DARK, spaceBefore=16, spaceAfter=8,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'H3', parent=styles['Heading3'],
        fontSize=13, textColor=HexColor("#333333"), spaceBefore=12, spaceAfter=6,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'BodyText2', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=6,
        fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'CodeBlock', parent=styles['Normal'],
        fontSize=8, leading=10, fontName='Courier',
        backColor=HexColor("#f4f4f4"), textColor=HexColor("#333333"),
        leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=6,
        borderWidth=1, borderColor=HexColor("#dddddd"), borderPadding=8
    ))
    styles.add(ParagraphStyle(
        'TipBox', parent=styles['Normal'],
        fontSize=9, leading=13, fontName='Helvetica',
        backColor=TIP_BG, leftIndent=10, rightIndent=10,
        spaceBefore=6, spaceAfter=6, borderWidth=1,
        borderColor=TIP_BORDER, borderPadding=8
    ))
    styles.add(ParagraphStyle(
        'InfoBox', parent=styles['Normal'],
        fontSize=9, leading=13, fontName='Helvetica',
        backColor=INFO_BG, leftIndent=10, rightIndent=10,
        spaceBefore=6, spaceAfter=6, borderWidth=1,
        borderColor=INFO_BORDER, borderPadding=8
    ))
    styles.add(ParagraphStyle(
        'TaskBox', parent=styles['Normal'],
        fontSize=9, leading=13, fontName='Helvetica',
        backColor=TASK_BG, leftIndent=10, rightIndent=10,
        spaceBefore=6, spaceAfter=6, borderWidth=1,
        borderColor=TASK_BORDER, borderPadding=8
    ))
    styles.add(ParagraphStyle(
        'DangerBox', parent=styles['Normal'],
        fontSize=9, leading=13, fontName='Helvetica',
        backColor=DANGER_BG, leftIndent=10, rightIndent=10,
        spaceBefore=6, spaceAfter=6, borderWidth=1,
        borderColor=DANGER_BORDER, borderPadding=8
    ))
    styles.add(ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontSize=9, leading=12, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontSize=9, leading=12, fontName='Helvetica-Bold', textColor=white
    ))

    return styles


def escape_xml(text):
    """Escape XML special characters for reportlab Paragraphs."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def process_inline_formatting(text):
    """Convert markdown inline formatting to reportlab XML."""
    # Bold + italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" size="9" color="#c7254e">\1</font>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'<font color="#007AFF"><u>\1</u></font>', text)
    return text


def parse_markdown_to_flowables(md_content, styles, section_title=None):
    """Parse markdown content and return a list of reportlab flowables."""
    flowables = []
    lines = md_content.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    code_lang = ""
    in_admonition = False
    admonition_type = ""
    admonition_lines = []
    admonition_indent = 0

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End code block
                code_text = escape_xml('\n'.join(code_lines))
                if code_text.strip():
                    flowables.append(Paragraph(
                        code_text.replace('\n', '<br/>'),
                        styles['CodeBlock']
                    ))
                code_lines = []
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
                code_lang = line.strip()[3:].split()[0] if len(line.strip()) > 3 else ""
                # Remove title="..." from lang
                code_lang = code_lang.split('"')[0]
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Admonitions (MkDocs style: !!! type "title")
        admonition_match = re.match(r'^!!! (\w+)(?:\s+"([^"]*)")?', line)
        if admonition_match:
            # Flush previous admonition
            if in_admonition and admonition_lines:
                flowables.extend(render_admonition(admonition_type, admonition_lines, styles))

            admonition_type = admonition_match.group(1)
            in_admonition = True
            admonition_lines = []
            admonition_indent = 4
            title = admonition_match.group(2)
            if title:
                admonition_lines.append(f"**{title}**")
            i += 1
            continue

        if in_admonition:
            if line.startswith('    ') or line.strip() == '':
                content = line[4:] if line.startswith('    ') else ''
                # Check for nested admonition
                nested_match = re.match(r'^    !!! (\w+)(?:\s+"([^"]*)")?', line)
                if nested_match:
                    nested_type = nested_match.group(1)
                    nested_title = nested_match.group(2) or ""
                    admonition_lines.append(f"**{nested_title}**" if nested_title else "")
                    i += 1
                    continue
                admonition_lines.append(content)
                i += 1
                continue
            else:
                # End of admonition
                flowables.extend(render_admonition(admonition_type, admonition_lines, styles))
                in_admonition = False
                admonition_lines = []
                # Don't increment i, process current line

        # Empty line
        if not line.strip():
            i += 1
            continue

        # Headers
        if line.startswith('# ') and not line.startswith('## '):
            text = process_inline_formatting(line[2:].strip())
            flowables.append(Paragraph(text, styles['H1']))
            # Add a line under H1
            flowables.append(HRFlowable(
                width="100%", thickness=2, color=PRIMARY,
                spaceBefore=0, spaceAfter=10
            ))
            i += 1
            continue

        if line.startswith('## '):
            text = process_inline_formatting(line[3:].strip())
            flowables.append(Paragraph(text, styles['H2']))
            i += 1
            continue

        if line.startswith('### '):
            text = process_inline_formatting(line[4:].strip())
            flowables.append(Paragraph(text, styles['H3']))
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

        # Images
        img_match = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
        if img_match:
            alt_text = img_match.group(1)
            img_path = img_match.group(2)
            # Clean path (remove mkdocs width directive)
            img_path = img_path.split('{')[0].strip()
            # Resolve relative path
            if img_path.startswith('../img/'):
                img_path = os.path.join(IMG_DIR, img_path.replace('../img/', ''))
            elif img_path.startswith('img/'):
                img_path = os.path.join(IMG_DIR, img_path.replace('img/', ''))

            if os.path.exists(img_path):
                try:
                    pil_img = PILImage.open(img_path)
                    img_width, img_height = pil_img.size
                    # Scale to max 200px width
                    max_w = 150
                    ratio = max_w / img_width
                    display_w = max_w
                    display_h = img_height * ratio
                    # Cap height
                    if display_h > 300:
                        display_h = 300
                        display_w = img_width * (300 / img_height)

                    img = Image(img_path, width=display_w, height=display_h)
                    img.hAlign = 'CENTER'
                    flowables.append(Spacer(1, 6))
                    flowables.append(img)
                    flowables.append(Spacer(1, 6))
                except Exception as e:
                    flowables.append(Paragraph(f"[Image: {alt_text}]", styles['BodyText2']))
            i += 1
            continue

        # List items
        list_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.+)', line)
        if list_match:
            indent = len(list_match.group(1))
            marker = list_match.group(2)
            content = list_match.group(3)
            content = process_inline_formatting(escape_xml(content))

            if marker in ['-', '*']:
                bullet = '\u2022'
            else:
                bullet = marker

            left_indent = 20 + indent * 10
            flowables.append(Paragraph(
                f"{bullet}  {content}",
                ParagraphStyle(
                    'ListItem', parent=styles['BodyText2'],
                    leftIndent=left_indent, firstLineIndent=0
                )
            ))
            i += 1
            continue

        # Regular paragraph
        text = process_inline_formatting(escape_xml(line.strip()))
        if text:
            flowables.append(Paragraph(text, styles['BodyText2']))
        i += 1

    # Flush remaining admonition
    if in_admonition and admonition_lines:
        flowables.extend(render_admonition(admonition_type, admonition_lines, styles))

    return flowables


def render_admonition(adm_type, lines, styles):
    """Render an admonition block."""
    flowables = []
    content = '\n'.join(lines).strip()
    if not content:
        return flowables

    # Remove nested admonition markers
    content = re.sub(r'^!!! \w+.*$', '', content, flags=re.MULTILINE)
    content = content.strip()

    # Process inline formatting
    processed = process_inline_formatting(escape_xml(content))
    processed = processed.replace('\n', '<br/>')

    type_map = {
        'tip': ('TipBox', 'Conseil'),
        'info': ('InfoBox', 'Info'),
        'example': ('TaskBox', 'Tache'),
        'danger': ('DangerBox', 'Important'),
        'warning': ('DangerBox', 'Attention'),
    }

    style_name, label = type_map.get(adm_type, ('InfoBox', adm_type.capitalize()))

    text = f"<b>{label}</b><br/>{processed}"
    flowables.append(Paragraph(text, styles[style_name]))

    return flowables


def render_table(table_lines, styles):
    """Render a markdown table."""
    flowables = []
    rows = []

    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if all(re.match(r'^[-:]+$', c) for c in cells):
            continue  # Skip separator
        rows.append(cells)

    if not rows:
        return flowables

    # Build table data
    table_data = []
    for row_idx, row in enumerate(rows):
        table_row = []
        for cell in row:
            cell_text = process_inline_formatting(escape_xml(cell))
            if row_idx == 0:
                table_row.append(Paragraph(cell_text, styles['TableHeader']))
            else:
                table_row.append(Paragraph(cell_text, styles['TableCell']))
        table_data.append(table_row)

    if not table_data:
        return flowables

    # Calculate column widths
    available_width = A4[0] - 4 * cm
    num_cols = len(table_data[0])
    col_width = available_width / num_cols

    table = Table(table_data, colWidths=[col_width] * num_cols)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
    ]))

    flowables.append(Spacer(1, 6))
    flowables.append(table)
    flowables.append(Spacer(1, 6))

    return flowables


def add_cover_page(flowables, styles):
    """Add a cover page."""
    flowables.append(Spacer(1, 6 * cm))

    # Title background
    title_data = [[Paragraph("TP React Native", styles['DocTitle'])]]
    title_table = Table(title_data, colWidths=[16 * cm])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
    ]))
    flowables.append(title_table)
    flowables.append(Spacer(1, 1 * cm))

    subtitle = Paragraph(
        "Applications mobiles avec React Native et Expo",
        ParagraphStyle('CoverSub', parent=styles['Normal'],
                       fontSize=14, textColor=HexColor("#666666"),
                       alignment=TA_CENTER)
    )
    flowables.append(subtitle)
    flowables.append(Spacer(1, 0.5 * cm))

    info = Paragraph(
        "UMONS - Informatique de Gestion",
        ParagraphStyle('CoverInfo', parent=styles['Normal'],
                       fontSize=12, textColor=HexColor("#999999"),
                       alignment=TA_CENTER)
    )
    flowables.append(info)
    flowables.append(Spacer(1, 2 * cm))

    # Table of contents
    toc_title = Paragraph("Table des matieres", ParagraphStyle(
        'TOCTitle', parent=styles['H2'], alignment=TA_CENTER
    ))
    flowables.append(toc_title)
    flowables.append(Spacer(1, 0.5 * cm))

    toc_items = [
        "0. Prerequisites",
        "1. Exercice 0 : Creer un projet",
        "2. Exercice 1 : Hello World (Counter)",
        "3. Exercice 2 : DevNotes",
        "4. Exercice 3 : DevHub",
    ]
    for item in toc_items:
        flowables.append(Paragraph(
            item,
            ParagraphStyle('TOCItem', parent=styles['BodyText2'],
                           fontSize=11, alignment=TA_CENTER, spaceAfter=4)
        ))

    flowables.append(PageBreak())


def add_page_number(canvas, doc):
    """Add page number to each page."""
    page_num = canvas.getPageNumber()
    if page_num > 1:  # Skip cover page
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor("#999999"))
        canvas.drawCentredString(A4[0] / 2, 1.5 * cm, f"Page {page_num - 1}")
        # Header line
        canvas.setStrokeColor(PRIMARY)
        canvas.setLineWidth(0.5)
        canvas.line(2 * cm, A4[1] - 1.5 * cm, A4[0] - 2 * cm, A4[1] - 1.5 * cm)
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(HexColor("#bbbbbb"))
        canvas.drawString(2 * cm, A4[1] - 1.3 * cm, "TP React Native - UMONS")
        canvas.restoreState()


def main():
    styles = get_styles()

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    flowables = []

    # Cover page
    add_cover_page(flowables, styles)

    # Document sections in order
    sections = [
        ("docs/prerequisites.md", None),
        ("docs/exercices/00-create-project.md", None),
        ("docs/exercices/01-hello-world.md", None),
        ("docs/exercices/02-devnotes.md", None),
        ("docs/exercices/03-devhub.md", None),
    ]

    for idx, (filepath, title) in enumerate(sections):
        full_path = os.path.join(BASE_DIR, filepath)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        section_flowables = parse_markdown_to_flowables(content, styles, title)
        flowables.extend(section_flowables)

        # Add page break between sections (except last)
        if idx < len(sections) - 1:
            flowables.append(PageBreak())

    doc.build(flowables, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
