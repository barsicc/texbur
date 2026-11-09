"""Схемы для ЛР5_защита.md (рисуются схематично, для перерисовки от руки)."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = os.path.join(os.path.dirname(__file__), "..", "рисунки")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight"); plt.close(fig)

# 1. Схема бурильной колонны
fig, ax = plt.subplots(figsize=(5.2, 7)); ax.set_xlim(0, 10); ax.set_ylim(0, 20); ax.axis("off")
parts = [  # (y0, y1, half-width, label)
    (18.6, 19.6, 0.5, "вертлюг"),
    (16.0, 18.6, 0.35, "ведущая труба (квадрат)"),
    (15.5, 16.0, 0.45, "переводники ведущей трубы\n(верхний, нижний, предохранительный)"),
    (9.0, 15.5, 0.3, "бурильные трубы + замки\n(+ протекторы)"),
    (8.6, 9.0, 0.45, "переводник"),
    (6.6, 8.6, 0.55, "УБТ 3-й ступени"),
    (4.6, 6.6, 0.7, "УБТ 2-й ступени"),
    (2.4, 4.6, 0.85, "УБТ 1-й ступени (наддолотная)"),
    (1.9, 2.4, 1.0, "центратор / калибратор"),
    (1.0, 1.9, 1.0, "долото"),
]
for y0, y1, w, lab in parts:
    ax.add_patch(plt.Rectangle((3 - w, y0), 2 * w, y1 - y0, fc="#ddd", ec="k"))
    ax.annotate(lab, (3 + w, (y0 + y1) / 2), (4.6, (y0 + y1) / 2), va="center", fontsize=9,
                arrowprops=dict(arrowstyle="-", lw=0.6))
ax.plot([1.6, 1.6], [1.0, 8.6], "k", lw=1); ax.text(1.4, 4.8, "КНБК", rotation=90, ha="right", va="center", fontsize=11, weight="bold")
ax.plot([1.6, 1.8], [1.0, 1.0], "k", lw=1); ax.plot([1.6, 1.8], [8.6, 8.6], "k", lw=1)
save(fig, "рис1_бурильная_колонна.png")

# 2. Эпюра осевой силы, нейтральное сечение
fig, ax = plt.subplots(figsize=(5.5, 5))
L, lu = 10, 3.0     # длина колонны, длина УБТ (условно)
qbt, qu, P = 1.0, 4.0, 9.0
z = np.linspace(0, L, 400)   # z — глубина от устья
def N(z):
    # сила растяжения (+) / сжатия (-) в сечении z: вес ниже сечения минус реакция забоя P
    w_below = np.where(z < L - lu, qbt * (L - lu - z) + qu * lu, qu * (L - z))
    return w_below - P
n = N(z)
ax.plot(n, z, "k", lw=2); ax.axvline(0, color="k", lw=0.8)
ax.fill_betweenx(z, 0, n, where=n >= 0, color="#9cf", alpha=.6, label="растяжение")
ax.fill_betweenx(z, 0, n, where=n < 0, color="#f99", alpha=.6, label="сжатие")
zn = L - P / qu
ax.axhline(zn, ls="--", color="b"); ax.text(ax.get_xlim()[1]*0.35, zn - 0.15, "нейтральное сечение (N = 0)", color="b", va="bottom")
ax.axhline(L - lu, ls=":", color="gray"); ax.text(ax.get_xlim()[1]*0.35, L - lu - 0.15, "верх УБТ", color="gray", va="bottom")
ax.invert_yaxis(); ax.set_ylabel("глубина"); ax.set_xlabel("осевая сила N  (← сжатие | растяжение →)")
ax.text(-P, L + 0.05, "−Pд\n(забой)", ha="center", va="top", fontsize=9)
ax.set_xticks([]); ax.set_yticks([0, L]); ax.set_yticklabels(["устье", "забой"]); ax.legend(loc="upper right")
ax.set_title("Осевая сила по длине колонны")
save(fig, "рис2_нейтральное_сечение.png")

# 3. Формы изгиба
fig, axs = plt.subplots(1, 3, figsize=(7.5, 5))
y = np.linspace(0, 1, 300)
titles = ["устойчивое\nположение", "плоский изгиб\n(синусоида)", "спиральный\n(винтовой) изгиб"]
for ax, t in zip(axs, titles):
    ax.plot([-1, -1], [0, 1], "k", lw=3); ax.plot([1, 1], [0, 1], "k", lw=3)
    ax.set_xlim(-1.4, 1.4); ax.axis("off"); ax.set_title(t, fontsize=10)
axs[0].plot(0 * y, y, "r", lw=2)
axs[1].plot(0.75 * np.sin(np.pi * 3 * y), y, "r", lw=2)
axs[2].plot(0.75 * np.sin(2 * np.pi * 4 * y), y, "r", lw=2)
axs[2].plot(0.75 * np.sin(2 * np.pi * 4 * y + np.pi/2) * 0, y, alpha=0)
for k in range(8):
    yy = (k + 0.25) / 4 / 2 + 0.0
for ax in axs: ax.annotate("", (0, -0.05), (0, 0.15), arrowprops=dict(arrowstyle="<-", lw=1.5))
axs[1].text(0.85, 0.5, "l — длина\nполуволны", fontsize=8)
axs[1].annotate("", (0.8, 0), (0.8, 1/3), arrowprops=dict(arrowstyle="<->", lw=0.8))
fig.text(0.5, 0.02, "стенки скважины — чёрные линии, ось колонны — красная; стрелка снизу — сжимающая сила (реакция забоя)", ha="center", fontsize=8)
save(fig, "рис3_формы_изгиба.png")

# 4. Саркисов: длина полуволны от z
fig, ax = plt.subplots(figsize=(5.5, 4))
EI_q = 1.0
zz = np.linspace(-6, 6, 300)
for w, ls in [(1.0, "-"), (2.0, "--"), (4.0, ":")]:
    l = 10 / w * np.sqrt(0.5 * zz + np.sqrt(0.25 * zz**2 + EI_q * w**2))
    ax.plot(zz, l, "k", ls=ls, label=f"ω{'' if w==1 else f' × {int(w)}'}")
ax.axvline(0, color="b", ls="--"); ax.text(0.1, ax.get_ylim()[1]*0.9, "нейтральное\nсечение", color="b", fontsize=8)
ax.set_xlabel("z  (← сжатая часть, ниже НС | растянутая часть, выше НС →)")
ax.set_ylabel("длина полуволны l"); ax.set_xticks([]); ax.set_yticks([])
ax.legend(title="частота вращения"); ax.set_title("Формула Саркисова (качественно)")
save(fig, "рис4_саркисов.png")
print("OK")
