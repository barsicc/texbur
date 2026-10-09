"""Рисунки для пояснительной записки ДЗ-1, вариант 2."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Ellipse, FancyArrowPatch
from matplotlib.ticker import FuncFormatter

from calc import SUB, LAYERS, RU, CEMENT, UNSTABLE_TO, SECTIONS, section_design

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "рисунки")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 12, "mathtext.fontset": "stix"})


def ru(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")


def layer_values():
    out = []
    for t, b, *_ in LAYERS:
        s = next(x for x in SUB if x["top"] == t)
        out.append(dict(top=t, bot=b, kf=s["kf"], kfr=s["kfr"]))
    return out


def fig_pressure():
    plt.rcParams.update({"font.size": 14})
    fig, ax = plt.subplots(figsize=(8.0, 8.8))
    lv = layer_values()
    # окно допустимых плотностей между KF и KFR
    for i, l in enumerate(lv):
        ax.fill_betweenx([l["top"], l["bot"]], l["kf"], l["kfr"], color="#dbe7f3", lw=0,
                         label="область $K_F < \\rho_R < K_{FR}$" if i == 0 else None)
    xs, ys = [], []
    for l in lv:
        xs += [l["kf"], l["kf"]]; ys += [l["top"], l["bot"]]
    ax.plot(xs, ys, color="black", lw=2.2, label="$K_F$")
    xs, ys = [], []
    for l in lv:
        xs += [l["kfr"], l["kfr"]]; ys += [l["top"], l["bot"]]
    ax.plot(xs, ys, color="black", lw=2.2, ls=(0, (6, 2)), label="$K_{FR}$")
    xs, ys = [], []
    for s in SUB:
        xs += [s["rr"], s["rr"]]; ys += [s["top"], s["bot"]]
    ax.plot(xs, ys, color="#1f4e79", lw=1.6, ls=(0, (2, 2)), label="$\\rho_R = K_S K_F$")
    for name, a, b in SECTIONS:
        d = section_design(a, b)
        ax.plot([d["rr"], d["rr"]], [a, b], color="#c00000", lw=1.3,
                label="$\\rho_R$, принятая в интервале бурения" if a == 0 else None)

    for z in (900, 1100, 1200, 2100):
        ax.axhline(z, color="0.65", lw=0.6, ls=":")
    ax.axhspan(0, UNSTABLE_TO, facecolor="none", edgecolor="0.6", hatch="..", lw=0)
    ax.text(1.47, 250, f"неустойчивые породы,\nсклонные к поглощениям\n(0–{UNSTABLE_TO} м)",
            fontsize=12, va="center", bbox=dict(facecolor="white", edgecolor="none", pad=1))

    # подписи пород справа от окна
    for t, b, rock, *_ in LAYERS:
        ax.text(1.98, 720 if t == 0 else (t + b) / 2, rock, fontsize=11.5, va="center", ha="right", color="0.3")

    # колонны
    xc = [2.05, 2.11, 2.17]
    for r, x in zip(sorted(RU, key=lambda r: r["depth"]), xc):
        ax.plot([x, x], [0, r["depth"]], color="black", lw=1.4)
        ax.plot([x - 0.012, x + 0.012], [r["depth"]] * 2, color="black", lw=1.4)
        ax.text(x, r["depth"] + 25, str(r["depth"]), ha="center", va="top", fontsize=12)
    ax.text(2.11, -70, "колонны", ha="center", va="bottom", fontsize=12)

    ax.set_xlim(0.7, 2.22)
    ax.set_ylim(2550, 0)
    ax.set_xticks([0.8, 1.0, 1.2, 1.4, 1.6, 1.8])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: ru(v)))
    ax.set_yticks(range(0, 2401, 300))
    ax.xaxis.tick_top(); ax.xaxis.set_label_position("top")
    ax.set_xlabel("$K_F$, $K_{FR}$, $\\rho_R$")
    ax.set_ylabel("Глубина z, м")
    ax.grid(True, color="0.92", lw=0.5)
    for sp in ("right", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.legend(loc="lower left", fontsize=11.5, framealpha=1)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис1_график_совмещенных_давлений.png"), dpi=200)
    plt.close(fig)


def fig_construction():
    """Схема конструкции в виде, принятом на занятиях (С01, стр. 19), со шкалой глубин."""
    fig, ax = plt.subplots(figsize=(7.4, 9.2))
    cols = sorted(RU, key=lambda r: r["depth"])
    cem = {c[0]: c for c in CEMENT}
    xs = [1.3, 2.2, 3.1]
    x_lab = 4.5
    ax.plot([0.75, 4.1], [0, 0], color="black", lw=2.2)
    # шкала глубин
    ax.plot([0.35, 0.35], [0, 2400], color="0.4", lw=0.8)
    for z in range(0, 2401, 300):
        ax.plot([0.3, 0.4], [z, z], color="0.4", lw=0.8)
        ax.text(0.27, z, str(z), ha="right", va="center", fontsize=12, color="0.3")
    ax.text(0.27, -70, "z, м", ha="right", va="center", fontsize=12, color="0.3")
    prev = 0
    for i, (r, x) in enumerate(zip(cols, xs), start=1):
        top_c = cem[r["name"]][1]
        ax.plot([x, x], [0, r["depth"]], color="black", lw=2.2)
        ax.plot([x - 0.17, x + 0.17], [r["depth"]] * 2, color="black", lw=2.6)
        for z in range(int(top_c) + 10, int(r["depth"]) - 25, 45):
            ax.plot([x - 0.21, x], [z + 30, z], color="black", lw=0.9)
        ax.text(x, -50, f"D{i}", ha="center", va="bottom", fontsize=15)
        ax.text(x - 0.24, r["depth"] + 15, f"L{i} = {r['depth']}", ha="right", va="center", fontsize=14)
        if top_c > 0:
            ax.plot([x - 0.12, x + 0.12], [top_c] * 2, color="black", lw=1.6)
            ax.text(x + 0.16, top_c, f"H{i} = {top_c}", ha="left", va="center", fontsize=14)
        zb = (prev + r["depth"]) / 2
        ax.annotate("", xy=(x + 0.03, zb), xytext=(x_lab - 0.05, zb),
                    arrowprops=dict(arrowstyle="-|>", lw=1.0, color="black"))
        ax.text(x_lab, zb, f"d{i}", ha="left", va="center", fontsize=15)
        prev = r["depth"]
    # расшифровка
    lines = [f"D{i} = {ru(r['D'])} мм,  L{i} = {r['depth']} м,  d{i} = {ru(r['db'])} мм"
             for i, r in enumerate(cols, start=1)]
    lines.append(f"H1 = H2 = 0 (до устья),  H3 = {cem[cols[2]['name']][1]} м")
    for k, t in enumerate(lines):
        ax.text(0.3, 2640 + k * 115, t, fontsize=14, va="center")
    ax.set_xlim(0.0, 5.2)
    ax.set_ylim(3110, -140)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис2_схема_конструкции.png"), dpi=200)
    plt.close(fig)


def fig_foreign():
    src = os.path.join(HERE, "..", "..", "..", "рисунки", "С01", "стр17_схема_подбора_диаметров_дюймы.png")
    img = mpimg.imread(src)
    h, w = img.shape[:2]
    fig, ax = plt.subplots(figsize=(w / 100, h / 100), dpi=100)
    ax.imshow(img)
    # 5" -> 6 1/8" -> 7 5/8" -> 9 1/2" -> 10 3/4" -> 12 1/4"
    nodes = [(257, 93), (274, 138), (319, 180), (362, 223), (330, 267), (340, 312)]
    for x, y in nodes:
        ax.add_patch(Ellipse((x, y), 56, 31, fill=False, edgecolor="#c00000", lw=2.2))
    for (x1, y1), (x2, y2) in zip(nodes, nodes[1:]):
        ax.add_patch(FancyArrowPatch((x1, y1 + 12), (x2, y2 - 12), arrowstyle="-|>", mutation_scale=11,
                                     color="#c00000", lw=1.5, shrinkA=2, shrinkB=2))
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(os.path.join(OUT, "рис3_зарубежная_схема_выбор.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_pressure()
    fig_construction()
    fig_foreign()
    print("ok")
