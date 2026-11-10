"""Схемы для ЛР6_защита.md (схематично, для перерисовки от руки).
рис5_формы_изгиба.png скопирован из ЛР5 (ЛР/ЛР5/src/figures.py)."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch
OUT = os.path.join(os.path.dirname(__file__), "..", "рисунки")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight"); plt.close(fig)

# 1. Колонна по секциям и эпюра растягивающей силы
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.5, 6.2), gridspec_kw=dict(width_ratios=[1, 1.5]), sharey=True)
# глубина: 0 устье, 10 забой
segs = [  # (верх, низ, полуширина, цвет, подпись)
    (0.0, 3.0, 0.32, "#c9d9f0", "секция 2\n(прочнее: группа Л)"),
    (3.0, 6.6, 0.28, "#dbe6f5", "секция 1\n(группа К)"),
    (6.6, 8.5, 0.34, "#eee", "НК\n(группа Д,\nтолстая стенка)"),
    (8.5, 10.0, 0.55, "#ccc", "КНБК\n(УБТ, ЗД, долото)"),
]
for y0, y1, w, c, lab in segs:
    a1.add_patch(Rectangle((-w, y0), 2 * w, y1 - y0, fc=c, ec="k"))
    a1.text(0.75, (y0 + y1) / 2, lab, va="center", fontsize=8.5)
a1.set_xlim(-1, 2.6); a1.invert_yaxis(); a1.axis("off")
a1.text(0, -0.25, "устье", ha="center"); a1.text(0, 10.35, "забой", ha="center")
# сила: на верху каждой секции растёт; линейно по длине
q = {0: 0.9, 1: 0.9, 2: 1.0, 3: 3.5}
y = np.linspace(0, 10, 500)
def Q(yy):
    tot = 0
    for (y0, y1, w, c, lab), k in zip(segs, range(4)):
        top, bot = max(y0, yy), y1
        if bot > top: tot += q[k] * (bot - top)
    return tot
qq = np.array([Q(v) for v in y])
a2.plot(qq, y, "k", lw=2); a2.fill_betweenx(y, 0, qq, color="#9cf", alpha=.5)
for yy, lab in [(3.0, "Qдоп(1)"), (0.0, "Qдоп(2)")]:
    a2.axvline(Q(yy), color="r", ls="--", lw=1, ymax=1)
    a2.text(Q(yy) - 0.15, 4.6 if yy else 1.3, lab + "\nверхнего сечения\nсекции " + ("1" if yy else "2"), color="r", ha="right", va="center", fontsize=8)
for s in (3.0, 6.6, 8.5): a2.axhline(s, color="gray", ls=":", lw=.8)
a2.set_xlabel("растягивающая сила Q  (при подъёме колонны)"); a2.set_xticks([]); a2.set_yticks([])
a2.set_xlim(0, Q(0) * 1.12); a2.set_title("Q растёт снизу вверх — наверху\nставят самые прочные трубы", fontsize=10)
save(fig, "рис1_секции_и_эпюра.png")

# 2. Концы бурильных труб: высадка внутрь, наружу, приварной замок (продольный полуразрез)
fig, axs = plt.subplots(1, 3, figsize=(8, 3.6))
def pipe_end(ax, kind):
    ax.set_xlim(0, 10); ax.set_ylim(-1.5, 3.4); ax.axis("off"); ax.set_aspect("equal")
    ax.plot([0, 10], [0, 0], "k-.", lw=.7)  # ось
    t, R = 0.5, 2.0   # стенка, наружный радиус тела
    if kind == "in":
        wall = [(0, R), (5, R), (5, R), (10, R), (10, R - 1.0), (6.5, R - 1.0), (5, R - t), (0, R - t)]
        ax.add_patch(Polygon(wall, fc="#bbb", ec="k"))
        ax.set_title("ТБВ — высадка внутрь", fontsize=10)
        ax.text(5, -0.25, "стенка утолщена внутрь,\nканал сужен", fontsize=8, ha="center", va="top")
    elif kind == "out":
        wall = [(0, R), (5, R), (6.5, R + 0.5), (10, R + 0.5), (10, R - t), (0, R - t)]
        ax.add_patch(Polygon(wall, fc="#bbb", ec="k"))
        ax.set_title("ТБН — высадка наружу", fontsize=10)
        ax.text(5, -0.25, "стенка утолщена наружу,\nканал не сужен", fontsize=8, ha="center", va="top")
    else:
        wall = [(0, R), (4.5, R), (4.5, R - t), (0, R - t)]
        ax.add_patch(Polygon(wall, fc="#bbb", ec="k"))
        ax.add_patch(Polygon([(4.5, R), (5.6, R + 0.9), (10, R + 0.9), (10, R - 0.9), (5.6, R - 0.9), (4.5, R - t)], fc="#8ab", ec="k"))
        ax.plot([4.5, 4.5], [R - t, R], "r", lw=3)
        ax.set_title("ТБПВ — приварной замок", fontsize=10)
        ax.text(5, -0.25, "замок приварен к трубе,\nрезьбы труба–замок нет", fontsize=8, ha="center", va="top"); ax.text(3.2, 3.05, "сварной шов", color="r", fontsize=8)
        ax.text(6.4, R - 0.25, "замок", fontsize=8)
    ax.text(0.3, R + 0.25, "тело трубы", fontsize=8)
for ax, k in zip(axs, ["in", "out", "weld"]): pipe_end(ax, k)
fig.text(0.5, 0.2, "показана верхняя половина продольного разреза конца трубы; штрихпунктир — ось трубы", ha="center", fontsize=8)
save(fig, "рис2_концы_труб.png")

# 3. Бурильный замок: ниппель + муфта
fig, ax = plt.subplots(figsize=(7, 3.6)); ax.set_xlim(0, 20); ax.set_ylim(-1.6, 5.2); ax.axis("off"); ax.set_aspect("equal")
ax.plot([0, 20], [0, 0], "k-.", lw=.7)
# труба слева, муфта, ниппель, труба справа
ax.add_patch(Polygon([(0, 2.0), (2.5, 2.0), (2.5, 1.5), (0, 1.5)], fc="#ddd", ec="k"))
muf = [(2.5, 1.5), (2.5, 3.3), (10, 3.3), (10, 2.6), (7, 1.7), (2.5, 1.5)]
ax.add_patch(Polygon([(2.5, 1.2), (2.5, 3.3), (10, 3.3), (10, 2.75), (6.6, 1.95), (6.6, 1.2)], fc="#9bd", ec="k"))
ax.add_patch(Polygon([(10, 3.3), (17.5, 3.3), (17.5, 1.2), (6.6, 1.2), (6.6, 1.75), (10, 2.55)], fc="#f3c38a", ec="k"))
ax.add_patch(Polygon([(17.5, 2.0), (20, 2.0), (20, 1.5), (17.5, 1.5)], fc="#ddd", ec="k"))
# резьба зубцами по конусу
xs = np.linspace(6.8, 9.8, 13)
for x in xs:
    yb = 1.75 + (x - 6.6) * (2.55 - 1.75) / 3.4
    ax.plot([x, x + 0.12, x + 0.24], [yb, yb + 0.15, yb], "k", lw=.6)
ax.plot([10, 10], [2.6, 3.3], "r", lw=3)
ax.text(6.0, 3.6, "муфта замка", ha="center"); ax.text(14, 3.6, "ниппель замка", ha="center")
ax.annotate("упорный торец\n(герметизирует и\nразгружает резьбу)", (10, 3.0), (11.2, 4.4), color="r", fontsize=8, arrowprops=dict(arrowstyle="->", color="r"))
ax.annotate("замковая резьба —\nкрупная, коническая", (8.3, 2.2), (6.5, -1.3), fontsize=8, arrowprops=dict(arrowstyle="->"))
ax.text(1.2, 2.2, "труба", ha="center", fontsize=8); ax.text(18.8, 2.2, "труба", ha="center", fontsize=8)
ax.annotate("трубная резьба\n(труба–муфта)", (2.5, 1.75), (0.0, 3.9), fontsize=7.5, arrowprops=dict(arrowstyle="->", lw=.6)); ax.annotate("трубная резьба\n(ниппель–труба)", (17.5, 1.75), (16.8, 4.3), fontsize=7.5, arrowprops=dict(arrowstyle="->", lw=.6))
save(fig, "рис3_замок.png")

# 4. Силы на трубу в наклонном стволе
fig, ax = plt.subplots(figsize=(5.8, 4.6)); ax.set_aspect("equal"); ax.axis("off")
al = np.radians(35)   # угол от вертикали
d = np.array([np.sin(al), -np.cos(al)])  # направление вниз по стволу
n = np.array([np.cos(al), np.sin(al)])   # нормаль к стенке (вверх от нижней стенки)
p0 = np.array([0, 0])
L = 6
ax.plot(*np.array([p0 - n * 0.6, p0 - n * 0.6 + d * L]).T, "k", lw=3)    # нижняя стенка
ax.plot(*np.array([p0 + n * 0.9, p0 + n * 0.9 + d * L]).T, "k", lw=3)    # верхняя стенка
c = p0 + d * 3
ax.add_patch(Polygon([c - d * 1.2 - n * 0.6, c + d * 1.2 - n * 0.6, c + d * 1.2, c - d * 1.2], fc="#bbb", ec="k"))
m = c - n * 0.3
def arr(p, v, col, lab, off=(0.1, 0.1)):
    ax.add_patch(FancyArrowPatch(p, p + v, arrowstyle="-|>", mutation_scale=14, color=col, lw=1.8))
    ax.text(*(p + v + np.array(off)), lab, color=col, fontsize=9)
arr(m, np.array([0, -2.4]), "k", "G = q·l\n(вес)", (-1.3, -0.6))
arr(m, d * 2.4 * np.cos(al), "b", "G·cosα\n(вдоль оси)", (0.6, 0.3))
arr(m, -n * 2.4 * np.sin(al), "g", "G·sinα\n(прижимает к стенке)", (-3.0, -0.7))
arr(c - n * 0.48 + d * 2.2, d * 1.3, "r", "Fтр = f·G·sinα\n(против движения)", (0.3, -0.4))
arr(c - d * 1.25 - n * 0.3, -d * 1.4, "m", "движение\nпри подъёме", (-2.2, 0.1))
ax.plot([0, 0], [0.3, -2.0], "k:", lw=.8); ax.text(0.15, -1.3, "α", fontsize=11)
ax.set_xlim(-4, 7); ax.set_ylim(-6.5, 1.5)
ax.set_title("Труба на наклонном участке ствола", fontsize=10)
save(fig, "рис4_наклонный_ствол.png")
print("OK")
