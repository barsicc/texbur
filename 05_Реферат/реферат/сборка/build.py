"""Сборка черновых DOCX/PDF и контрольной копии без служебных блоков."""

import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor
import fitz

SOURCES = Path(__file__).resolve().parents[1] / "текст"
FILES = (
    "00_титул.md", "01_введение.md", "02_глава1.md", "03_глава2.md",
    "04_глава3.md", "05_глава4.md", "06_заключение.md", "07_литература.md",
)
STEM = "Математические_модели_процесса_бурения_черновик"
TEXT_WIDTH = 170
TABLE_WIDTHS = {
    1: (40, 65, 65),
    2: (78, 40, 52),
    3: (17, 17, 17, 17, 17, 17, 17, 17, 17, 17),
    4: (51, 17, 27, 27, 22, 26),
    5: (21, 25, 29, 63, 32),
}


def xml(tag, attributes=None):
    element = OxmlElement(tag)
    for key, value in (attributes or {}).items():
        element.set(qn(key), str(value))
    return element


def field(paragraph, part, value=None):
    run = paragraph.add_run()
    if part == "instruction":
        element = xml("w:instrText")
        element.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        element.text = value
    else:
        element = xml("w:fldChar", {"w:fldCharType": part})
    run._r.append(element)


def configure_style(doc, name, *, size=12, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                    indent=0, line=1.5, before=0, after=0, bold=False, keep=False):
    if name not in doc.styles:
        doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    style = doc.styles[name]
    style.base_style = doc.styles["Normal"] if name != "Normal" else None
    style.font.name = "Times New Roman"
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.font.bold = bold
    style.font.italic = False
    props = style._element.get_or_add_rPr()
    fonts = props.find(qn("w:rFonts"))
    for key in list(fonts.attrib):
        del fonts.attrib[key]
    for kind in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn("w:" + kind), "Times New Roman")
    lang = props.find(qn("w:lang"))
    if lang is None:
        lang = xml("w:lang")
        props.append(lang)
    lang.set(qn("w:val"), "ru-RU")
    paragraph = style.paragraph_format
    paragraph.alignment = alignment
    paragraph.first_line_indent = Mm(indent)
    paragraph.line_spacing = line
    paragraph.space_before = Pt(before)
    paragraph.space_after = Pt(after)
    paragraph.widow_control = True
    paragraph.keep_with_next = keep
    paragraph.keep_together = False
    return style


def set_styles(doc):
    for name in ("Normal", "Body Text", "First Paragraph"):
        configure_style(doc, name, indent=12.5)
    for name in ("Heading 1", "Heading 2"):
        configure_style(doc, name, alignment=WD_ALIGN_PARAGRAPH.LEFT, before=12,
                        after=6, bold=True, keep=True)
        doc.styles[name].paragraph_format.keep_together = True
    center = WD_ALIGN_PARAGRAPH.CENTER
    configure_style(doc, "Title Block", alignment=center)
    configure_style(doc, "Contents Title", alignment=center, bold=True, after=12, keep=True)
    configure_style(doc, "TOC 1", alignment=WD_ALIGN_PARAGRAPH.LEFT, line=1.0)
    configure_style(doc, "TOC 2", alignment=WD_ALIGN_PARAGRAPH.LEFT, line=1.0)
    configure_style(doc, "Captioned Figure", alignment=center, before=4, keep=True)
    configure_style(doc, "Image Caption", size=10, alignment=center, line=1.15, after=6)
    configure_style(doc, "Table Heading", size=11, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                    before=6, after=4, line=1.15, keep=True)
    configure_style(doc, "Table Cell", size=10, line=1.15, alignment=WD_ALIGN_PARAGRAPH.LEFT)
    configure_style(doc, "Equation Block", alignment=WD_ALIGN_PARAGRAPH.LEFT)
    configure_style(doc, "Bibliography Entry", alignment=WD_ALIGN_PARAGRAPH.LEFT, line=1.24, after=4)
    configure_style(doc, "Footer", alignment=center, line=1)
    hyperlink = doc.styles["Hyperlink"]
    hyperlink.font.name = "Times New Roman"
    hyperlink.font.color.rgb = RGBColor(0, 0, 0)


def page_style(doc, control):
    section = doc.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    (section.top_margin, section.bottom_margin, section.left_margin,
     section.right_margin) = (Mm(20), Mm(20), Mm(20), Mm(20))
    section.footer_distance = Mm(9)
    section.different_first_page_header_footer = not control
    footer = section.footer.paragraphs[0]
    footer.style = "Footer"
    field(footer, "begin")
    field(footer, "instruction", " PAGE ")
    field(footer, "separate")
    footer.add_run("2" if not control else "1")
    field(footer, "end")


def number_equations(doc, numbers):
    blocks = [p for p in doc.paragraphs if p._p.find(qn("m:oMathPara")) is not None]
    if len(blocks) != len(numbers):
        raise ValueError(f"Формулы в источнике и DOCX: {len(numbers)} и {len(blocks)}")
    for paragraph, number in zip(blocks, numbers):
        block = paragraph._p.find(qn("m:oMathPara"))
        math = block.find(qn("m:oMath"))
        paragraph._p.remove(block)
        paragraph.style = "Equation Block"
        tabs = paragraph.paragraph_format.tab_stops
        tabs.add_tab_stop(Mm(TEXT_WIDTH / 2), WD_TAB_ALIGNMENT.CENTER)
        tabs.add_tab_stop(Mm(TEXT_WIDTH), WD_TAB_ALIGNMENT.RIGHT)
        paragraph.paragraph_format.keep_together = True
        paragraph.add_run("\t")
        paragraph._p.append(math)
        paragraph.add_run(f"\t({number})")


def layout_tables(doc):
    captions = [p for p in doc.paragraphs if re.match(r"Таблица [1-5] —", p.text)]
    for caption in captions:
        caption.style = "Table Heading"
    for number, table in enumerate(doc.tables, start=1):
        table.autofit = False
        table.alignment = 1
        widths = TABLE_WIDTHS[number]
        if len(widths) != len(table.columns):
            # A text table with a wider set of fields can use equal columns.
            widths = [TEXT_WIDTH / len(table.columns)] * len(table.columns)
        for col, width in zip(table.columns, widths):
            col.width = Mm(width)
        for index, row in enumerate(table.rows):
            props = row._tr.get_or_add_trPr()
            props.append(xml("w:cantSplit"))
            if index == 0:
                props.append(xml("w:tblHeader"))
            for column, (cell, width) in enumerate(zip(row.cells, widths)):
                cell.width = Mm(width)
                if index == 0:
                    cell._tc.get_or_add_tcPr().append(xml("w:shd", {"w:fill": "EDEDED"}))
                for paragraph in cell.paragraphs:
                    paragraph.style = "Table Cell"
                    if number >= 3 and column > 0:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    paragraph.paragraph_format.keep_with_next = number in (1, 3) and index < len(table.rows) - 1
                    if index == 0:
                        for run in paragraph.runs:
                            run.bold = True
        borders = xml("w:tblBorders")
        for side in ("top", "bottom", "insideH"):
            borders.append(xml("w:" + side, {"w:val": "single", "w:sz": 4, "w:color": "AAAAAA"}))
        for side in ("left", "right", "insideV"):
            borders.append(xml("w:" + side, {"w:val": "nil"}))
        props = table._tbl.tblPr
        previous = props.find(qn("w:tblBorders"))
        if previous is not None:
            props.remove(previous)
        props.insert_element_before(borders, "w:shd", "w:tblLayout")


def add_toc(doc, headings, pages):
    first = headings[0]
    first.paragraph_format.page_break_before = True
    title = first.insert_paragraph_before("Содержание", "Contents Title")
    title.paragraph_format.page_break_before = True
    entries = []
    for index, heading in enumerate(headings):
        level = int(heading.style.name[-1])
        bookmark_name = f"referat_heading_{index}"
        heading._p.insert(1, xml("w:bookmarkStart", {"w:id": 1000 + index,
                                                     "w:name": bookmark_name}))
        heading._p.append(xml("w:bookmarkEnd", {"w:id": 1000 + index}))
        entry = first.insert_paragraph_before(style=f"TOC {level}")
        entry.paragraph_format.left_indent = Mm(0 if level == 1 else 5)
        entry.paragraph_format.tab_stops.add_tab_stop(
            Mm(TEXT_WIDTH), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        entries.append(entry)
        if index == 0:
            field(entry, "begin")
            field(entry, "instruction", r' TOC \o "1-2" \h \z ')
            field(entry, "separate")
        link = xml("w:hyperlink", {"w:anchor": bookmark_name})
        run = xml("w:r")
        content = xml("w:t")
        content.text = heading.text
        run.append(content)
        link.append(run)
        entry._p.append(link)
        entry.add_run("\t" + str(pages[index]))
    field(entries[-1], "end")


def layout_doc(doc, numbers, pages=None, control=False):
    set_styles(doc)
    page_style(doc, control)
    number_equations(doc, numbers)
    layout_tables(doc)
    headings = [p for p in doc.paragraphs if p.style.name in ("Heading 1", "Heading 2")]
    if not control:
        title = doc.paragraphs[:9]
        if title[-1].text != "Москва, 2026":
            raise ValueError("Состав титульного листа изменён")
        for idx, paragraph in enumerate(title):
            paragraph.style = "Title Block"
            paragraph.paragraph_format.space_before = Pt({0: 12, 2: 100, 5: 95, 8: 115}.get(idx, 0))
            if idx in (2, 4):
                for run in paragraph.runs:
                    run.bold = True
                    run.font.size = Pt(14)
            if 5 <= idx <= 7:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                paragraph.paragraph_format.left_indent = Mm(78)
        headings[-1].paragraph_format.page_break_before = True
        all_paragraphs = doc.paragraphs
        bibliography = next(i for i, p in enumerate(all_paragraphs) if p._p is headings[-1]._p)
        for paragraph in all_paragraphs[bibliography + 1:]:
            paragraph.style = "Bibliography Entry"
        add_toc(doc, headings, pages or [3] * len(headings))
    return [heading.text for heading in headings]


def extract_markdown(control):
    selected = FILES[1:-1] if control else FILES
    sections = [(SOURCES / file).read_text(encoding="utf-8") for file in selected]
    markdown = "\n\n".join(sections)
    numbers = [int(number) for number in re.findall(r"\\tag\{(\d+)\}", markdown)]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError(f"Нумерация формул: {numbers}")
    return markdown, numbers


def norm(value):
    return " ".join(value.replace("\u00ad", "").split())


def heading_pages(pdf, headings):
    with fitz.open(pdf) as doc:
        text = [norm(page.get_text()) for page in doc][2:]
    pages = []
    for title in headings:
        found = [index + 3 for index, page_text in enumerate(text) if norm(title) in page_text]
        if len(found) != 1:
            raise ValueError(f"Заголовок {title!r}: страницы {found}")
        pages.append(found[0])
    return pages


def convert(office, profile, source, output):
    target = output / f"{source.stem}.pdf"
    if target.exists():
        target.unlink()
    subprocess.run([office, f"-env:UserInstallation={profile.as_uri()}", "--headless",
                    "--convert-to", "pdf:writer_pdf_Export", "--outdir", str(output),
                    str(source)], check=True)
    if not target.is_file():
        raise RuntimeError(f"LibreOffice не создал {target}")


def assemble(args):
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="texbur-stage4-") as temp:
        scratch = Path(temp)
        markdown, numbers = extract_markdown(args.control)
        draft = scratch / "source.docx"
        command = ["pandoc", "-f", "markdown-smart", "-t", "docx", "--fail-if-warnings",
                   "--resource-path", str(SOURCES), "-M", "lang=ru-RU",
                   "-o", str(draft)]
        if args.control:
            command.extend(["--lua-filter", str(Path(__file__).with_name("text_only.lua"))])
        subprocess.run(command, input=markdown, text=True, cwd=SOURCES, check=True)
        if args.control:
            stem = "контроль_объёма"
        else:
            stem = STEM
        docx = output / f"{stem}.docx"
        pdf = output / f"{stem}.pdf"
        profile = scratch / "office"
        pages = None
        for attempt in range(4):
            document = Document(draft)
            headings = layout_doc(document, numbers, pages, args.control)
            document.core_properties.title = "Математические модели процесса бурения"
            document.core_properties.author = ""
            document.core_properties.last_modified_by = ""
            document.core_properties.comments = ""
            document.save(docx)
            convert(args.office, profile, docx, output)
            if args.control:
                break
            actual = heading_pages(pdf, headings)
            if actual == pages:
                for title, page in zip(headings, actual):
                    print(f"{page:2d} {title}")
                break
            pages = actual
        else:
            raise RuntimeError("Разбиение на страницы после обновления содержания нестабильно")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--office", default=os.environ.get("TEXBUR_SOFFICE", "soffice"))
    parser.add_argument("--control", action="store_true", help="Экспорт основного текста для замера.")
    assemble(parser.parse_args())


if __name__ == "__main__":
    main()
