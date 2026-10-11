"""Пояснительная записка ДЗ-1 (Word): Markdown + LaTeX -> pandoc (формулы — редактор формул Word) -> оформление python-docx."""
import os
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from calc import (SUB, LAYERS, RU, CEMENT, SECTIONS, section_design, COND_DEPTH, INTER_DEPTH,
                  PROD_DEPTH, G, RHO_W, WALL_CHOICE, OTTM, SMALL_DELTA)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIG = os.path.join(ROOT, "рисунки")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "ДЗ1_вар17_пояснительная_записка.docx")

STUDENT = "Фамилия И.О."
GROUP = "РТ\u201123\u201112"


def f(x, nd=3):
    return f"{x:.{nd}f}".replace(".", ",")


def m(x, nd=1):
    return f"{x:.{nd}f}".replace(".", "{,}")  # для LaTeX


PB = "\\newpage"  # заменяется на разрыв страницы

L = []
add = L.append

# ------------------------------------------------------------------ титул
add('::: {custom-style="Титул"}')
add("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n")
add("РОССИЙСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ НЕФТИ И ГАЗА\n(НАЦИОНАЛЬНЫЙ ИССЛЕДОВАТЕЛЬСКИЙ УНИВЕРСИТЕТ)\nИМЕНИ И.М. ГУБКИНА\n")
add("Кафедра бурения нефтяных и газовых скважин\n")
add(":::")
add('::: {custom-style="ТитулОтступ"}\n \n:::')
add('::: {custom-style="ТитулЗаголовок"}')
add("ДОМАШНЕЕ ЗАДАНИЕ № 1\n")
add(":::")
add('::: {custom-style="Титул"}')
add("по дисциплине «Технология бурения скважин»\n")
add("Тема: «Проектирование конструкции скважины»\n")
add("Вариант № 17\n")
add(":::")
add('::: {custom-style="ТитулОтступ"}\n \n:::')
add('::: {custom-style="ТитулПодписи"}')
add(f"Выполнил: студент группы {GROUP}\n")
add(f"[[{STUDENT}]]\n")
add(" \n")
add("Преподаватель: доцент, к.т.н.\n")
add("Балицкий В.П.\n")
add(":::")
add('::: {custom-style="ТитулОтступ"}\n \n:::')
add('::: {custom-style="Титул"}')
add("Москва 2026")
add(":::")
add(PB)

add("# ВВЕДЕНИЕ {.unnumbered}")
add("В работе по заданным геологическим условиям проектируется конструкция нефтяной скважины глубиной "
    "2100 м: определяются число и глубины спуска обсадных колонн, интервалы их цементирования, диаметры "
    "колонн и долот; результат сравнивается с подбором диаметров по зарубежной методике. Расчёты выполнены "
    "в Excel (прилагаемый файл).")

# ------------------------------------------------------------------ 1
add("# Исходные данные и индексы давлений")
add("## Исходные данные")
add("Назначение скважины — нефтяная; глубина — 2100 м; диаметр эксплуатационной колонны — 114,3 мм. "
    "В интервале 0–250 м залегают неустойчивые породы, склонные к поглощениям. Разрез и давления — "
    "в таблице 1; давления отнесены к подошве интервала.")
add('::: {custom-style="ПодписьТаблицы"}\nТаблица 1 – Горные породы и пластовые давления\n:::')
add("| Порода | Интервал, м | Пластовое давление, МПа | Давление поглощения, МПа |")
add("|:---:|:---:|:---:|:---:|")
for t, b, rock, pf, pfr in LAYERS:
    add(f"| {rock} | {t}–{b} | {f(pf,1)} | {f(pfr,1)} |")
add("")
add("## Расчёт индексов давлений")
add("Индекс пластового давления (коэффициент аномальности) и индекс давления поглощения:")
add(r"$$K_F = \frac{P_F}{\rho_w \cdot g \cdot z}, \qquad (1)$$")
add(r"$$K_{FR} = \frac{P_{FR}}{\rho_w \cdot g \cdot z}, \qquad (2)$$")
add(r"где $P_F$, $P_{FR}$ — пластовое давление и давление поглощения, Па; $\rho_w = 1000$ кг/м³ — плотность воды; "
    r"$g = 9{,}81$ м/с²; $z$ — глубина, м.")
add("Относительная плотность бурового раствора по Правилам безопасности [4, п. 2.7.3.3]:")
add(r"$$\rho_R = K_S \cdot K_F, \qquad (3)$$")
add(r"где $K_S$ — коэффициент безопасности, равный 1,1 в интервале 0–1200 м и 1,05 ниже 1200 м "
    r"(превышение гидростатического давления над пластовым не менее 10 и 5 % соответственно).")
s4 = SUB[4]
add("Например, для известняка (1900–2100 м):")
add(rf"$$K_F = \frac{{27{{,}}3 \cdot 10^6}}{{1000 \cdot 9{{,}}81 \cdot 2100}} = {m(s4['kf'],3)}, \quad "
    rf"K_{{FR}} = \frac{{30{{,}}5 \cdot 10^6}}{{1000 \cdot 9{{,}}81 \cdot 2100}} = {m(s4['kfr'],3)}, \quad "
    rf"\rho_R = 1{{,}}05 \cdot {m(s4['kf'],3)} = {m(s4['rr'],3)}.$$")
add("Песчаник (1000–1900 м) пересекает глубину 1200 м, поэтому разбит на участки 1000–1200 и 1200–1900 м "
    "с разными $K_S$. Результаты — в таблице 2 (плотность раствора $\\rho_m = \\rho_R \\cdot \\rho_w$).")
add('::: {custom-style="ПодписьТаблицы"}\nТаблица 2 – Результаты расчёта индексов давлений\n:::')
add("| Интервал, м | $K_F$ | $K_{FR}$ | $K_S$ | $\\rho_R$ | $\\rho_m$, кг/м³ |")
add("|:---:|:---:|:---:|:---:|:---:|:---:|")
for s in SUB:
    add(f"| {s['top']}–{s['bot']} | {f(s['kf'])} | {f(s['kfr'])} | {f(s['ks'],2)} | {f(s['rr'])} | {f(s['rr']*1000,0)} |")
add("")
add("Глины (800–1000 м) имеют пластовое давление ниже гидростатического ($K_F = 0{,}897$); расчётная "
    "$\\rho_R = 0{,}987$ для них не применяется — интервал проходится раствором вышележащих пород.")

# ------------------------------------------------------------------ 2
d1 = section_design(0, COND_DEPTH)
d2 = section_design(COND_DEPTH, INTER_DEPTH)
d3 = section_design(INTER_DEPTH, PROD_DEPTH)
add("# Число и глубины спуска обсадных колонн")
add("## Совмещённый график давлений")
add("Совмещённый график давлений (рисунок 1) показывает изменение $K_F$, $K_{FR}$ и $\\rho_R$ по глубине. "
    "Весь необсаженный ствол бурится раствором одной плотности, которая должна удовлетворять условию")
add(r"$$K_F < \rho_R < K_{FR} \qquad (4)$$")
add("одновременно для всех вскрытых интервалов. Интервалы, для которых такой плотности не существует, "
    "разделяются обсадной колонной.")
add("![](рисунки/рис1_совмещенный_график.png){width=14cm}")
add('::: {custom-style="ПодписьРисунка"}\nРисунок 1 – Совмещённый график давлений\n:::')
add(f"Из графика видно, что для бурения песчаника и известняка (1000–2100 м) требуется "
    f"$\\rho_R = {m(d3['rr'],3)}$, что превышает индексы давления поглощения пород выше 1000 м "
    f"({f(SUB[0]['kfr'])} и {f(SUB[1]['kfr'])}). С другой стороны, раствор, допустимый для интервала 0–1000 м "
    f"($\\rho_R = {m(d2['rr'],3)}$), легче, чем требуется для песчаника ($K_F = {m(SUB[2]['kf'],3)}$), — "
    "при его вскрытии возникнет нефтегазоводопроявление. Таким образом, условия бурения интервалов "
    "0–1000 и 1000–2100 м несовместимы.")
add("## Принятая конструкция")
add(f"1. Кондуктор спускается на глубину **{COND_DEPTH} м** — на 10 м ниже подошвы неустойчивых пород (250 м), "
    "чтобы перекрыть зону возможных поглощений и обвалов.")
add(f"2. Промежуточная колонна спускается на глубину **{INTER_DEPTH} м** — до кровли песчаника с аномально "
    "высоким пластовым давлением; башмак устанавливается в непроницаемых глинах. Спуск ниже 1000 м недопустим: "
    f"бурение песчаника раствором $\\rho_R = {m(d2['rr'],3)}$ приведёт к проявлению.")
add(f"3. Эксплуатационная колонна спускается до забоя — **{PROD_DEPTH} м**.")
add("")
add('::: {custom-style="ПодписьТаблицы"}\nТаблица 3 – Плотность бурового раствора по интервалам бурения\n:::')
add("| Интервал бурения, м | Под колонну | $\\rho_R$ | $\\rho_m$, кг/м³ | Проверка (4) |")
add("|:----------:|:----------------:|:------:|:------:|:----------------------:|")
for (name, a, b), col in zip(SECTIONS, ["кондуктор", "промежуточную", "эксплуатационную"]):
    d = section_design(a, b)
    add(f"| {a}–{b} | {col} | {f(d['rr'])} | {f(d['rr']*1000,0)} | {f(d['kf_max'])} < {f(d['rr'])} < {f(d['kfr_min'])} |")
add("")

# ------------------------------------------------------------------ 3
add("# Интервалы цементирования")
add("Интервалы цементирования определены по Правилам безопасности [4, п. 2.7.4.10–2.7.4.11]: кондуктор "
    "цементируется до устья; для нефтяных скважин тампонажный раствор поднимается не менее чем на 150 м над "
    "башмаком предыдущей колонны и над кровлей продуктивного горизонта; цементное кольцо должно быть сплошным.")
add('::: {custom-style="ПодписьТаблицы"}\nТаблица 4 – Интервалы цементирования обсадных колонн\n:::')
add("| Колонна | Глубина спуска, м | Кровля цемента, м | Обоснование |")
add("|:---:|:---:|:---:|:---|")
add(f"| Кондуктор | {COND_DEPTH} | 0 | до устья |")
add(f"| Промежуточная | {INTER_DEPTH} | 110 | {COND_DEPTH} − 150 = 110 м |")
add(f"| Эксплуатационная | {PROD_DEPTH} | 850 | {INTER_DEPTH} − 150 = 850 м |")
add("")
add("Цемент за эксплуатационной колонной (850–2100 м) перекрывает продуктивный известняк с запасом "
    "1050 м над кровлей (требуется не менее 150 м) и песчаник с АВПД; интервал 850–1000 м обеспечивает "
    "перекрытие с промежуточной колонной.")

# ------------------------------------------------------------------ 4
rp, ri, rc = RU
add("# Диаметры долот и обсадных колонн")
add("## Расчёт диаметров")
add("Диаметры определяются последовательно снизу вверх. Расчётный диаметр долота:")
add(r"$$D_B = d_m + 2\Delta, \qquad (5)$$")
add(r"где $d_m$ — наружный диаметр муфты обсадной трубы ОТТМ по ГОСТ 632-80 [2], мм; $\Delta$ — минимальный "
    r"радиальный зазор между муфтой и стенкой скважины [1] (8 мм для колонн 114–127 мм, 13 мм для 168–245 мм, "
    r"18 мм для 273–299 мм). Диаметр долота принимается по ГОСТ 20692-2003 [3] — ближайший не меньший. "
    r"Внутренний диаметр вышележащей колонны должен пропускать это долото:")
add(r"$$d_i \ge D_B + 2\delta, \qquad (6)$$")
add(r"где $\delta = 5$ мм — минимальный зазор между долотом и внутренней стенкой колонны.")
add('::: {custom-style="ПодписьТаблицы"}\nТаблица 5 – Расчёт диаметров колонн и долот\n:::')
add("| Величина | Эксплуатационная | Промежуточная | Кондуктор |")
add("|:-------------------------|:--------:|:--------:|:--------:|")
add(f"| Требуемый $d_i$ по (6), мм | — | ≥ {f(ri['di_min_this'],1)} | ≥ {f(rc['di_min_this'],1)} |")
add(f"| Наружный диаметр $D$, мм | {f(rp['D'],1)} | {f(ri['D'],1)} | {f(rc['D'],1)} |")
add(f"| Толщина стенки / внутр. диаметр, мм | — | {f(WALL_CHOICE['Промежуточная'],1)} / 159,4 | {f(WALL_CHOICE['Кондуктор'],1)} / 252,7 |")
add(f"| Диаметр муфты $d_m$, мм | {f(rp['dm'],1)} | {f(ri['dm'],1)} | {f(rc['dm'],1)} |")
add(f"| Зазор $\\Delta$, мм | {rp['delta']} | {ri['delta']} | {rc['delta']} |")
add(f"| $D_B$ по (5), мм | {f(rp['db_calc'],1)} | {f(ri['db_calc'],1)} | {f(rc['db_calc'],1)} |")
add(f"| Долото по ГОСТ 20692, мм | **{f(rp['db'],1)}** | **{f(ri['db'],1)}** | **{f(rc['db'],1)}** |")
add("")
add(f"Пояснения к таблице 5. Для промежуточной колонны трубы 168,3 мм не проходят (d ≤ 153,7 мм < 156,0 мм); "
    "у труб 177,8 мм проход долота 146,0 мм обеспечивают толщины стенки 6,9…10,4 мм, принята 9,2 мм. "
    "Для кондуктора трубы 244,5 мм не проходят (d ≤ 228,7 мм < 232,3 мм), принята колонна 273,1 мм "
    "со стенкой 10,2 мм. Толщины стенок предварительные и уточняются расчётом колонн на прочность.")
add("## Схема конструкции скважины")
add("Схема конструкции приведена на рисунке 2 в обозначениях, принятых на практических занятиях [1].")
add("![](рисунки/рис2_схема_конструкции.png){width=11.5cm}")
add('::: {custom-style="ПодписьРисунка"}\nРисунок 2 – Схема конструкции скважины\n:::')

# ------------------------------------------------------------------ 5
add("# Проверка по зарубежной методике")
add("Зарубежная методика подбирает диаметры по схеме соответствия обсадных колонн и долот [1], "
    "двигаясь от эксплуатационной колонны (рисунок 3). Использованы стрелки стандартного зазора "
    "(Standard); размеры переведены из дюймов в миллиметры.")
add("![](рисунки/рис3_зарубежная_схема_выбор.png){width=16.5cm}")
add('::: {custom-style="ПодписьРисунка"}\nРисунок 3 – Схема подбора диаметров по зарубежной методике\n:::')
add('::: {custom-style="ПодписьТаблицы"}\nТаблица 6 – Сравнение отечественной и зарубежной методик\n:::')
add("| Колонна | Отечественная: колонна / долото, мм | Зарубежная: колонна / долото, мм |")
add("|:-----------:|:-------------:|:-------------:|")
add("| Эксплуатационная | 114,3 / 146,0 | 114,3 (4 1/2\") / 152,4 (6\") |")
add("| Промежуточная | 177,8 / 222,3 | 177,8 (7\") / 215,9 (8 1/2\") |")
add("| Кондуктор | 273,1 / 349,2 | 244,5 (9 5/8\") / 311,2 (12 1/4\") |")
add("")
add("Зарубежная методика даёт такие же диаметры эксплуатационной и промежуточной колонн. Расхождение "
    "возникает под промежуточной колонной: долото 8 1/2\" (215,9 мм) оставляет между муфтой 194,5 мм и стенкой "
    "скважины зазор 10,7 мм, что меньше нормативных 13 мм, поэтому по отечественной методике выбрано долото "
    "222,3 мм. Оно не проходит в колонну 244,5 мм (её наибольший внутренний диаметр 228,7 мм), отсюда кондуктор "
    "273,1 мм вместо 244,5 мм и долото 349,2 мм вместо 311,2 мм. Под эксплуатационную колонну зарубежная схема "
    "даёт, наоборот, большее долото — 152,4 мм (такого диаметра нет в ГОСТ 20692-2003).")
add("Следовательно, результат зарубежной методики аналогичен отечественному для двух нижних колонн, а для "
    "верхней части скважины она даёт более компактную конструкцию за счёт меньших допускаемых зазоров. "
    "Отечественная методика консервативнее: большие зазоры облегчают спуск колонн и улучшают качество "
    "цементирования.")

# ------------------------------------------------------------------ заключение
add("# ЗАКЛЮЧЕНИЕ {.unnumbered}")
add("Для нефтяной скважины глубиной 2100 м (вариант № 17) получены следующие результаты:")
add(f"- плотность бурового раствора: $\\rho_R = {m(d2['rr'],2)}$ ({f(d2['rr']*1000,0)} кг/м³) в интервале 0–1000 м "
    f"и $\\rho_R = {m(d3['rr'],2)}$ ({f(d3['rr']*1000,0)} кг/м³) в интервале 1000–2100 м;")
add("- конструкция из трёх колонн: кондуктор 273,1 мм на 260 м (долото 349,2 мм), промежуточная 177,8 мм "
    "на 1000 м (долото 222,3 мм), эксплуатационная 114,3 мм на 2100 м (долото 146,0 мм);")
add("- интервалы цементирования: 0–260, 110–1000 и 850–2100 м;")
add("- по зарубежной методике совпадают две нижние колонны, кондуктор получается меньше — 244,5 мм.")

add("# СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ {.unnumbered}")
add('::: {custom-style="Литература"}')
for i, t in enumerate([
    "Проектирование конструкции скважины: материалы практического занятия № 1 по дисциплине «Технология бурения скважин». — М.: РГУ нефти и газа (НИУ) имени И.М. Губкина, кафедра бурения нефтяных и газовых скважин.",
    "ГОСТ 632-80. Трубы обсадные и муфты к ним. Технические условия.",
    "ГОСТ 20692-2003. Долота шарошечные. Технические условия.",
    "Правила безопасности в нефтяной и газовой промышленности (ПБ 08-624-03).",
], 1):
    add(f"{i}. {t}")
add(":::")


parts = []
for line in L:
    if parts and line.startswith("|") and parts[-1].startswith("|"):
        parts[-1] += "\n" + line
    else:
        parts.append(line)
md = "\n\n".join(parts)
md = md.replace(PB, '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```')
md = md.replace("[[TOC]]", '```{=openxml}\n<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
                '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-2" \\h \\z \\u </w:instrText></w:r>'
                '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>Для обновления содержания нажмите F9 (правой кнопкой → Обновить поле).</w:t></w:r>'
                '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>\n```')

tmp = tempfile.mkdtemp()
md_path = os.path.join(tmp, "note.md")
open(md_path, "w", encoding="utf-8").write(md)
raw = os.path.join(tmp, "raw.docx")
subprocess.run(["pandoc", md_path, "-f", "markdown+pipe_tables+tex_math_dollars+raw_attribute+fenced_divs",
                "-o", raw, "--resource-path", ROOT, "--number-sections"], check=True)

# ================================================================== оформление
doc = Document(raw)
TNR = "Times New Roman"


def set_font(style, size=14, bold=None, italic=None):
    style.font.name = TNR
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(a), TNR)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rfonts.get(qn(a)) is not None:
            del rfonts.attrib[qn(a)]


def para_fmt(style, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=1.25, before=0, after=0, spacing=1.5, keep_next=False):
    pf = style.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Cm(indent) if indent else Cm(0)
    pf.left_indent = Cm(0)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = spacing
    pf.keep_with_next = keep_next


class _Styles:
    def __init__(self, st):
        self._st = st

    def __iter__(self):
        return iter(self._st)

    def __getitem__(self, name):
        for x in self._st:
            if x.name == name:
                return x
        raise KeyError(name)


styles = _Styles(doc.styles)
for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if name in [s.name for s in styles]:
        set_font(styles[name])
        para_fmt(styles[name])
for name, lvl in (("Heading 1", 1), ("Heading 2", 2)):
    st = styles[name]
    set_font(st, 14, bold=True, italic=False)
    para_fmt(st, WD_ALIGN_PARAGRAPH.LEFT, indent=1.25, before=12, after=12, keep_next=True)
custom = {
    "Титул": dict(align=WD_ALIGN_PARAGRAPH.CENTER, size=14, bold=False),
    "ТитулЗаголовок": dict(align=WD_ALIGN_PARAGRAPH.CENTER, size=20, bold=True),
    "ТитулПодписи": dict(align=WD_ALIGN_PARAGRAPH.LEFT, size=14, bold=False, left=8.0),
    "ТитулОтступ": dict(align=WD_ALIGN_PARAGRAPH.CENTER, size=14, bold=False, before=60),
    "ПодписьТаблицы": dict(align=WD_ALIGN_PARAGRAPH.LEFT, size=14, bold=False, before=6, keep=True),
    "ПодписьРисунка": dict(align=WD_ALIGN_PARAGRAPH.CENTER, size=14, bold=False, after=6),
    "Литература": dict(align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=14, bold=False),
}
for name, o in custom.items():
    if name not in [s.name for s in styles]:
        continue
    st = styles[name]
    set_font(st, o["size"], bold=o["bold"])
    para_fmt(st, o["align"], indent=0, before=o.get("before", 0), after=o.get("after", 0),
             keep_next=o.get("keep", False))
    if o.get("left"):
        st.paragraph_format.left_indent = Cm(o["left"])
if "Литература" in [s.name for s in styles]:
    styles["Литература"].paragraph_format.first_line_indent = Cm(1.25)

# поля и колонтитул с номером страницы (на титуле номера нет)
for sec in doc.sections:
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin, sec.right_margin = Cm(3), Cm(1.5)
    sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)
    sec.different_first_page_header_footer = True
    fp = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.first_line_indent = Cm(0)
    run = fp.add_run()
    for t, txt in (("begin", None), (None, " PAGE "), ("end", None)):
        if t:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), t); run._r.append(el)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = txt; run._r.append(el)
    run.font.name = TNR
    run.font.size = Pt(12)

# абзацы с формулами и рисунками — по центру, без отступа; списки — без лишних отступов
for p in doc.paragraphs:
    xml = p._p.xml
    if "<m:oMathPara" in xml or "<w:drawing" in xml:
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if "<w:drawing" in xml:
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(6)
    # выделить заглушку ФИО
    for r in p.runs:
        if "[[" in r.text:
            r.text = r.text.replace("[[", "").replace("]]", "")
            hl = OxmlElement("w:highlight"); hl.set(qn("w:val"), "yellow")
            r._r.get_or_add_rPr().append(hl)

# таблицы: сетка, 12 пт, одинарный интервал, по центру
def borders(tbl):
    tblPr = tbl._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6"); e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000")
        b.append(e)
    old = tblPr.find(qn("w:tblBorders"))
    if old is not None:
        tblPr.remove(old)
    tblPr.append(b)


for tbl in doc.tables:
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(tbl)
    tblW = tbl._tbl.tblPr.find(qn("w:tblW"))
    if tblW is not None:
        tblW.set(qn("w:type"), "pct"); tblW.set(qn("w:w"), "5000")
    for ri, row in enumerate(tbl.rows):
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_after = Pt(0)
                if p.paragraph_format.alignment is None:
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.size = Pt(12)
                    r.font.name = TNR
                    if ri == 0:
                        r.font.bold = True

# строки таблиц не разрываются, таблица держится целиком
for tbl in doc.tables:
    n = len(tbl.rows)
    for ri, row in enumerate(tbl.rows):
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        if ri < n - 1:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True

# отступ после таблиц
for tbl in doc.tables:
    nxt = tbl._tbl.getnext()
    if nxt is not None and nxt.tag == qn("w:p"):
        pPr = nxt.get_or_add_pPr()
        sp = pPr.find(qn("w:spacing"))
        if sp is None:
            sp = OxmlElement("w:spacing"); pPr.append(sp)
        sp.set(qn("w:before"), "160")

doc.core_properties.author = STUDENT
doc.core_properties.title = "ДЗ-1. Проектирование конструкции скважины. Вариант 7 (№ 17)"
doc.save(OUT)
print("saved", OUT)


# ---- десятичные числа в формулах: «9», «,», «81» -> одно число «9,81» без математического пробела после запятой
def _fix_decimal_commas(path):
    import re
    import shutil
    import zipfile
    tmp_path = path + ".tmp"
    pat = re.compile(r'<m:r>(?:<m:rPr>(?:<m:sty m:val="p"/>)?</m:rPr>)?<m:t>(\d+)</m:t></m:r>'
                     r'<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t>,</m:t></m:r>'
                     r'<m:r>(?:<m:rPr>(?:<m:sty m:val="p"/>)?</m:rPr>)?<m:t>(\d+)</m:t></m:r>')
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                xml = data.decode("utf-8")
                xml, n = pat.subn(r'<m:r><m:rPr><m:nor/></m:rPr><m:t>\1,\2</m:t></m:r>', xml)
                print("decimal commas fixed:", n)
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp_path, path)


_fix_decimal_commas(OUT)
