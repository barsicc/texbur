"""ЛР-6, вариант 7: расчёт бурильной колонны на прочность по секциям (шаблон пособия, стр. 55-56)."""
import datetime
import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.worksheet.pagebreak import Break

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "ЛР6_вар7.xlsx")

wb = Workbook()
ws = wb.active
ws.title = "Лист1"

thin = Side(style="thin")
med = Side(style="medium")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center")
A = "Arial"

for col, w in zip("ABCDEFGHIJKLM", [14, 9, 9, 12, 12, 7, 9, 9, 9, 9, 11, 9, 9]):
    ws.column_dimensions[col].width = w


def put(cell, value, size=10, bold=False, italic=False, align=CENTER, fmt=None, name=A):
    c = ws[cell]
    c.value = value
    c.font = Font(name=name, size=size, bold=bold, italic=italic)
    c.alignment = align
    if fmt:
        c.number_format = fmt
    return c


def frame(rng):
    for row in ws[rng]:
        for c in row:
            c.border = BOX


# ---------- Лист 1: исходные данные ----------
put("A1", datetime.date(2026, 10, 26), align=LEFT, fmt="DD.MM.YYYY")
ws.merge_cells("B2:L2")
put("B2", "Расчет бурильной колонны на прочность по секциям ( для вертикальной скважины )",
    size=12, bold=True, italic=True)
put("A4", "Фамилия", size=12, align=LEFT)
put("B4", "..............................", size=8, align=LEFT)
put("E4", "Группа", size=12, align=CENTER)
put("G4", "РТ-23-12", size=12, align=LEFT)
put("A6", "Вариант", size=12, align=LEFT)
put("B6", 7, size=12, align=LEFT)

ws.merge_cells("A8:E8")
put("A8", "Исходные данные", bold=True, italic=True)
ws.merge_cells("G8:K8")
put("G8", "Исходные данные", bold=True, italic=True)

left = [
    ("№ п/п", "Название", "Индивид. задание"),
    (1, "Способ\nбурения", "турбинный"),
    (2, "Условия бурения", "нормальные"),
    (3, "Глубина разбурива-\nемого интервала, м", 2750),
    (4, "Диаметр\nдолота,  м", 0.2159),
    (5, "Диаметр бурильных труб,\nм", 0.127),
    (6, "Длина наддолотного\nкомплекта, м", 400),
]
right = [
    ("№ п/п", "Название", "Индивид. задание"),
    (7, "Плотность материала\nБТ, кг/м3", 7850),
    (8, "Плотность промывоч-\nной жидкости,  кг/м3", 1200),
    (9, "Общая длина\nКНБК, м", 148.6),
    (10, "Общий вес\nКНБК,  кН", 165.54),
    (11, "Перепад давления\nв долоте, МПа", 4),
    (12, "Тип забойного\nдвигателя", "ЗТСШ-195"),
    (13, "Перепад давления в\nзабойном двигателе,\nМпа", 6.0),
]
for i, (n, name, val) in enumerate(left):
    r = 9 + i
    ws.merge_cells(f"B{r}:D{r}")
    put(f"A{r}", n, bold=True, italic=True)
    put(f"B{r}", name, bold=True, italic=True)
    put(f"E{r}", val, size=8 if r == 9 else 9, bold=(r == 9), italic=(r == 9))
    frame(f"A{r}:E{r}")
for i, (n, name, val) in enumerate(right):
    r = 9 + i
    ws.merge_cells(f"H{r}:J{r}")
    put(f"G{r}", n, bold=True, italic=True)
    put(f"H{r}", name, bold=True, italic=True)
    put(f"K{r}", val, size=8 if r == 9 else 9, bold=(r == 9), italic=(r == 9))
    frame(f"G{r}:K{r}")
frame("A8:E8")
frame("G8:K8")
ws["E15"].number_format = "0"
ws["K12"].number_format = "0.0"
ws["K13"].number_format = "0.00"
ws["K16"].number_format = "0.0"
ws.merge_cells("A16:B16")
put("A16", "Кзап = 1,4", align=LEFT)

ws.row_dimensions[2].height = 18
ws.row_dimensions[4].height = 18
ws.row_dimensions[6].height = 18
ws.row_dimensions[9].height = 30
for r in range(10, 16):
    ws.row_dimensions[r].height = 30
ws.row_dimensions[16].height = 45

# ---------- Лист 2: результаты расчета ----------
TNR = "Times New Roman"
put("A23", "=A1", name=TNR, align=LEFT, fmt="DD.MM.YYYY")
ws.merge_cells("E23:I23")
put("E23", "Результаты расчета", size=12, name=TNR)
put("A24", "Фамилия", size=11, name=TNR, align=LEFT)
put("B24", "......................", name=TNR, align=LEFT)
put("D24", "Вариант", name=TNR, align=LEFT)
put("E24", "=B6", name=TNR, align=LEFT)

put("A27", "секция\n\nпоказатели", size=7, align=Alignment(horizontal="center", vertical="center", wrap_text=True))
for col, h in zip("BCDEFGHIJKL", ["НК", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
    put(f"{col}27", h, name=TNR)

labels = {
    28: "Тип труб",
    29: "Толщина стенок,\nм",
    30: "Группа прочности\nстали",
    31: "Предельно\nрастягивающая\nнагрузка, 10⁴ Н",
    32: "Масса 1 м трубы,\nкг",
    33: "Площадь попереч.\nсечения канала\nтруб, м²",
    34: "Длина секции, м",
    35: "Уточненная длина\nсекции, м",
    36: "Вес, кН",
    37: "Нарастающая\nдлина\nпо секциям, м",
    38: "Общий вес\nколонны, кН",
    39: "Длина\nинструмента\nв целом, м",
}
for r, t in labels.items():
    put(f"A{r}", t, size=8)

# трубы: НК — ТБВК 0,127, гр. "Д", макс. толщина 0,01; секции — по табл. 6, 7 приложения
pipes = {
    "B": ("ТБВК", 0.01, "д", "-", 32.0, "-"),
    "C": ("ТБВК", 0.009, "к", 167, 29.3, 93.3),
    "D": ("ТБВК", 0.009, "е", 184, 29.3, "-"),
}
for col, (typ, s, grp, qp, q, f) in pipes.items():
    put(f"{col}28", typ, size=8)
    put(f"{col}29", s, size=8)
    put(f"{col}30", grp, size=8)
    put(f"{col}31", qp, size=8)
    put(f"{col}32", q, size=8, fmt="0.0")
    put(f"{col}33", f, size=8, fmt="0.0")
for col in "EFGHIJKL":
    put(f"{col}33", "-", size=8)

K = "(1-$K$11/$K$10)"
put("B34", "=E15", size=8, fmt="0")
put("C34", f"=(0.8*C31*10^4/1.4-1.1*($K$13+B36)*1000-($K$16+$K$14)*10^6*C33*10^-4)/(1.1*9.81*C32*{K})",
    size=8, fmt="0.00")
put("D34", f"=(0.8*D31*10^4/1.4-0.8*C31*10^4/1.4)/(1.1*9.81*D32*{K})", size=8, fmt="0.00")

put("B35", "=B34", size=8, fmt="0.00")
for prev, col in (("B", "C"), ("C", "D")):
    put(f"{col}35",
        f'=IF({prev}37+{col}34>$E$12,$E$12-{prev}37,IF({col}34<250,"выберите трубы с большей прочностью",FLOOR({col}34,25)))',
        size=8, fmt="0.00")

for col in "BCD":
    put(f"{col}36", f"=9.81*{col}35*{col}32*{K}/1000", size=8, fmt="0.00")

put("B37", "=K12+B35", size=8, fmt="0.00")
put("C37", "=B37+C35", size=8, fmt="0.00")
put("D37", "=C37+D35", size=8, fmt="0.00")

put("B38", "=K13+B36", size=8, fmt="0.00")
put("C38", "=B38+C36", size=8, fmt="0.00")
put("D38", "=C38+D36", size=8, fmt="0.00")

put("B39", "=D37", size=8, fmt="0.00")
ws.merge_cells("C39:L39")
put("C39", '=IF(ROUND(B39,2)=E12,"Расчет завершен.","")', size=8)

frame("A27:L39")
for c in ws["A27:L27"][0]:
    c.border = Border(left=thin, right=thin, top=med, bottom=med)
ws["A27"].border = Border(left=thin, right=thin, top=med, bottom=med, diagonal=thin, diagonalDown=True)

heights = {27: 30, 28: 13, 29: 24, 30: 33, 31: 45, 32: 24, 33: 45, 34: 24, 35: 33, 36: 13, 37: 33, 38: 24, 39: 35}
for r, h in heights.items():
    ws.row_dimensions[r].height = h

ws.print_area = "A1:M39"
ws.row_breaks.append(Break(id=22))
ws.page_setup.orientation = "landscape"
ws.page_setup.paperSize = ws.PAPERSIZE_A4
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
wb.calculation.fullCalcOnLoad = True

wb.save(OUT)
print(OUT)
