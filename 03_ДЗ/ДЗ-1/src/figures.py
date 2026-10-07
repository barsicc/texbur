"""Рисунки для пояснительной записки ДЗ-1."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, FancyArrowPatch
import matplotlib.image as mpimg

from matplotlib.ticker import FuncFormatter
from calc import (SUB, LAYERS, RU, CEMENT, COND_DEPTH, INTER_DEPTH, PROD_DEPTH, UNSTABLE_TO, FOREIGN,
                  SECTIONS, section_design)


def ru(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")

OUT = os.path.join(os.path.dirname(__file__), "..", "рисунки")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "Liberation Serif",
    "font.size": 12,
    "mathtext.fontset": "stix",
})


def steps(key, intervals):
    xs, ys = [], []
    for s in intervals:
        xs += [s[key], s[key]]
        ys += [s["top"], s["bot"]]
    return xs, ys


def fig_pressure():
    fig, ax = plt.subplots(figsize=(8.2, 8.6))
    layer_iv = [dict(top=t, bot=b, kf=SUB[[s["top"] for s in SUB].index(t)]["kf"],
                     kfr=SUB[[s["top"] for s in SUB].index(t)]["kfr"]) for t, b, *_ in LAYERS]
    x, y = steps("kf", layer_iv)
    ax.plot(x, y, color="black", lw=2.2, label=r"$K_F$ — индекс пластового давления")
    x, y = steps("kfr", layer_iv)
    ax.plot(x, y, color="black", lw=2.2, ls=(0, (1, 0)), alpha=0.55,
            label=r"$K_{FR}$ — индекс давления поглощения")
    x, y = steps("rr", SUB)
    ax.plot(x, y, color="black", lw=1.6, ls="--", label=r"$\rho_R$ — относительная плотность раствора")

    # принятая плотность раствора по интервалам бурения (секциям)
    first = True
    for name, a, b in SECTIONS:
        d = section_design(a, b)
        ax.plot([d["rr"], d["rr"]], [a, b], color="black", lw=1.0, ls="-.",
                label=r"$\rho_R$ принятая для интервала бурения" if first else None)
        first = False
    for b in [800, 1000, 1200, 1900, 2100]:
        ax.axhline(b, color="0.6", lw=0.6, ls=":")
    ax.axhspan(0, UNSTABLE_TO, color="0.85", zorder=0)
    ax.text(1.27, 125, "неустойчивые породы,\nсклонные к поглощениям\n(0–250 м)", fontsize=9.5,
            va="center")

    # подписи кривых
    ax.annotate(r"$K_F$", xy=(1.2769, 1500), xytext=(1.10, 1600), fontsize=14,
                arrowprops=dict(arrowstyle="-", lw=0.8))
    ax.annotate(r"$K_{FR}$", xy=(1.5291, 1450), xytext=(1.62, 1300), fontsize=14,
                arrowprops=dict(arrowstyle="-", lw=0.8))
    ax.annotate(r"$\rho_R$", xy=(1.3407, 1650), xytext=(1.15, 1800), fontsize=14,
                arrowprops=dict(arrowstyle="-", lw=0.8))

    # колонны справа
    xc = {"Кондуктор": 1.86, "Промежуточная": 1.93, "Эксплуатационная": 2.0}
    for r in RU:
        xx = xc[r["name"]]
        ax.plot([xx, xx], [0, r["depth"]], color="black", lw=1.4)
        ax.plot([xx - 0.012, xx + 0.012], [r["depth"], r["depth"]], color="black", lw=1.4)
        ax.text(xx, r["depth"] + 25, f"{r['depth']}", ha="center", va="top", fontsize=11)
    ax.text(1.93, -60, "Колонны", ha="center", va="bottom", fontsize=10)

    ax.set_xlim(0.8, 2.06)
    ax.set_ylim(2250, 0)
    ax.set_xticks([0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: ru(v)))
    ax.set_yticks(range(0, 2201, 200))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.set_xlabel(r"$K_F$; $K_{FR}$; $\rho_R$")
    ax.set_ylabel("Глубина z, м")
    ax.grid(True, color="0.9", lw=0.5)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.legend(loc="lower left", fontsize=10, framealpha=1)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис1_совмещенный_график_давлений.png"), dpi=200)
    plt.close(fig)


def fig_construction():
    fig, ax = plt.subplots(figsize=(8.2, 10))
    # горизонтальный масштаб: мм -> условные единицы
    k = 1.0
    cols = sorted(RU, key=lambda r: r["depth"])  # кондуктор, промежуточная, эксплуатационная
    cem = {c[0]: c for c in CEMENT}
    prev_shoe = 0
    prev_inner = None
    for r in cols:
        R_hole = r["db"] / 2 * k
        R_cas = r["D"] / 2 * k
        top_c = cem[r["name"]][1]
        # ствол (открытый) от башмака предыдущей колонны
        ax.plot([-R_hole, -R_hole], [prev_shoe, r["depth"]], color="0.35", lw=1, ls="-")
        ax.plot([R_hole, R_hole], [prev_shoe, r["depth"]], color="0.35", lw=1, ls="-")
        ax.plot([-R_hole, R_hole], [r["depth"], r["depth"]], color="0.35", lw=0.8, ls=":")
        # цемент: между ОК и стенкой (ниже башмака пред.) или пред. ОК (выше)
        for side in (-1, 1):
            # интервал в открытом стволе
            a, b = max(top_c, prev_shoe), r["depth"]
            if b > a:
                x0 = side * R_cas if side < 0 else R_cas
                w = R_hole - R_cas
                ax.add_patch(Rectangle((-R_hole if side < 0 else R_cas, a), w, b - a,
                                       facecolor="0.8", edgecolor="0.5", hatch="////", lw=0.3))
            # интервал внутри предыдущей колонны
            if prev_inner is not None and top_c < prev_shoe:
                w = prev_inner - R_cas
                ax.add_patch(Rectangle((-prev_inner if side < 0 else R_cas, top_c), w, prev_shoe - top_c,
                                       facecolor="0.8", edgecolor="0.5", hatch="////", lw=0.3))
        # колонна
        for side in (-1, 1):
            ax.plot([side * R_cas, side * R_cas], [0, r["depth"]], color="black", lw=2.4)
            ax.plot([side * R_cas, side * (R_cas + 6)], [r["depth"], r["depth"]], color="black", lw=2.4)
        prev_shoe = r["depth"]
        prev_inner = R_cas - 6

    ax.axhline(0, color="black", lw=1.5)
    ax.axvline(0, color="0.5", lw=0.6, ls="-.")

    # подписи
    lab_x = 200
    texts = {
        "Кондуктор": "1 — кондуктор",
        "Промежуточная": "2 — промежуточная колонна",
        "Эксплуатационная": "3 — эксплуатационная колонна",
    }
    for r in cols:
        top_c = cem[r["name"]][1]
        txt = (f"{texts[r['name']]}\nØ {ru(r['D'])} мм, L = {r['depth']} м\n"
               f"долото Ø {ru(r['db'])} мм\nцемент: {top_c}–{r['depth']} м")
        y = r["depth"] - (120 if r["name"] != "Кондуктор" else 40)
        ax.annotate(txt, xy=(r["D"] / 2, r["depth"] - 30), xytext=(lab_x, y), fontsize=10.5,
                    va="center", arrowprops=dict(arrowstyle="-", lw=0.7))
    # глубины слева
    for d in sorted({COND_DEPTH, INTER_DEPTH, PROD_DEPTH, 500}):
        ax.text(-205, d, f"{d} м", va="center", ha="right", fontsize=10.5)
        ax.plot([-200, -185], [d, d], color="black", lw=0.8)
    ax.text(-205, 25, "0 м", va="center", ha="right", fontsize=10.5)

    ax.set_xlim(-260, 420)
    ax.set_ylim(2200, -60)
    ax.axis("off")
    ax.add_patch(Rectangle((215, 2080), 20, 50, facecolor="0.8", edgecolor="0.5", hatch="////", lw=0.3))
    ax.text(240, 2105, "цементный камень", va="center", fontsize=10)
    ax.text(240, 2160, "горизонтальный масштаб условный", va="center", fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис2_схема_конструкции.png"), dpi=200)
    plt.close(fig)


def fig_foreign():
    src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "рисунки", "С01",
                       "стр17_схема_подбора_диаметров_дюймы.png")
    img = mpimg.imread(src)
    h, w = img.shape[:2]
    fig, ax = plt.subplots(figsize=(w / 100, h / 100), dpi=100)
    ax.imshow(img)
    # узлы цепочки 4 1/2" -> 6" -> 7" -> 8 1/2" -> 9 5/8" -> 12 1/4" (координаты в пикселях исходника)
    nodes = [(158, 93), (200, 138), (192, 180), (193, 224), (197, 268), (338, 312)]
    for x, y in nodes:
        ax.add_patch(Ellipse((x, y), 54, 30, fill=False, edgecolor="red", lw=2.2))
    for (x1, y1), (x2, y2) in zip(nodes, nodes[1:]):
        ax.add_patch(FancyArrowPatch((x1, y1 + 12), (x2, y2 - 12), arrowstyle="-|>", mutation_scale=12,
                                     color="red", lw=1.6, shrinkA=2, shrinkB=2))
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(os.path.join(OUT, "рис3_зарубежная_схема_выбор.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_pressure()
    fig_construction()
    fig_foreign()
    print("ok")
