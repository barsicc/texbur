"""Построение семи рисунков этапа 4. Расчётные данные этапа 2 читаются напрямую."""

import json
from io import StringIO
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np

PROJECT = Path(__file__).resolve().parents[2]
CALC = PROJECT / "расчеты"
OUTPUT = PROJECT / "реферат" / "текст" / "иллюстрации"
sys.path.insert(0, str(CALC / "скрипты"))
from leonov import read_inputs
from plot_leonov import cost_grid, sensitivity

INK = "#252a33"
BLUE = "#164d77"
RUST = "#9b3e25"
ROCK = "#e4ddd1"
STEEL = "#d5e4ed"
PALE = "#f3f5f7"


def sheet(width, height):
    return plt.subplots(figsize=(width / 25.4, height / 25.4), layout="constrained")


def arrow(ax, start, end, color=INK):
    ax.annotate("", xy=end, xytext=start,
                arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.2,
                            "mutation_scale": 10})


def contact():
    fig, axes = plt.subplots(1, 2, figsize=(160 / 25.4, 65 / 25.4), layout="constrained")
    ax, bx = axes
    for panel, title in zip(axes, ("Внедрение и скол", "Резание и трение")):
        panel.set(xlim=(0, 10), ylim=(0, 7.3), title=title)
        panel.axis("off")

    ax.add_patch(patches.Polygon([(0, .6), (10, .6), (10, 3), (7.1, 3),
                                  (5.2, 2.2), (4.2, 2.05), (3.1, 3), (0, 3)],
                                 facecolor=ROCK, edgecolor=INK))
    ax.add_patch(patches.Polygon([(3.4, 5.9), (5.05, 5.9), (5.05, 3.65),
                                  (4.55, 2.35), (4.05, 2.12), (3.4, 3.6)],
                                 facecolor=STEEL, edgecolor=INK))
    ax.add_patch(patches.Polygon([(5.55, 3.2), (7.16, 3.84), (6.26, 4.32)],
                                 facecolor=ROCK, edgecolor=RUST))
    arrow(ax, (2.55, 5.92), (2.55, 4.17), BLUE)
    ax.text(2.16, 6.2, "Нагрузка", ha="center", color=BLUE)
    ax.text(5.4, 5.35, "Вставка")
    ax.text(7.05, 4.48, "Скол", color=RUST)
    ax.text(6, 1.1, "Лунка")
    ax.plot([5.8, 5], [1.45, 2.2], color=INK, lw=.7)

    bx.add_patch(patches.Polygon([(0, .6), (10, .6), (10, 3.1), (6.4, 3.1),
                                  (5.25, 2.12), (0, 2.12)],
                                 facecolor=ROCK, edgecolor=INK))
    bx.add_patch(patches.Polygon([(2.7, 5.6), (4.35, 5.6), (5.35, 2.14),
                                  (4.1, 2.14), (3.1, 3.5)],
                                 facecolor=STEEL, edgecolor=INK))
    bx.add_patch(patches.Polygon([(5.65, 3.15), (6.05, 4.35), (7.55, 4.58),
                                  (6.93, 3.65)], facecolor=ROCK, edgecolor=RUST))
    bx.plot([4.15, 5.33], [2.14, 2.14], color=RUST, lw=3)
    arrow(bx, (4.55, 5.95), (7.5, 5.95), BLUE)
    bx.text(6.0, 6.22, "Движение", ha="center", color=BLUE)
    bx.text(1.58, 4.3, "Резец")
    bx.text(7.15, 4.85, "Стружка", color=RUST)
    bx.text(5.55, 1.05, "Площадка износа", color=RUST)
    bx.plot([5.45, 4.72], [1.45, 2.08], color=RUST, lw=.8)
    return fig


def operating_conditions():
    fig, axes = plt.subplots(1, 2, figsize=(160 / 25.4, 65 / 25.4), layout="constrained")
    panels = (
        ("Осевая нагрузка, $P$", "Рост внедрения", "Замедление\nроста"),
        ("Расход раствора, $Q$", "Недостаточная\nочистка", "Достаточная\nочистка"),
    )
    x = np.linspace(.08, .94, 200)
    for ax, (label, rising, flat), rate in zip(axes, panels, (4.0, 5.0)):
        ax.set(xlim=(0, 1.02), ylim=(0, 1.04))
        ax.axis("off")
        arrow(ax, (.11, .13), (.99, .13))
        arrow(ax, (.11, .13), (.11, 1))
        ax.text(.55, .01, label, ha="center")
        ax.text(.036, .57, "Механическая скорость", ha="center", va="center", rotation=90)
        y = .20 + .62 * (1 - np.exp(-rate * (x - .08)))
        ax.plot(x + .065, y, color=BLUE, lw=1.8, clip_on=False)
        ax.text(.42, .29, rising, ha="center")
        ax.text(.77, .88, flat, ha="center", va="bottom")
    return fig


def box(ax, xy, text, width, height, fill=PALE):
    x, y = xy
    ax.add_patch(patches.FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height,
        boxstyle="round,pad=0.03,rounding_size=0.08", facecolor=fill,
        edgecolor=BLUE, linewidth=1))
    ax.text(x, y, text, ha="center", va="center")


def model_types():
    fig, ax = sheet(160, 70)
    ax.set(xlim=(0, 12), ylim=(0, 5.7))
    ax.axis("off")
    box(ax, (6, 5.16), r"Нагрузка $P$, частота $n$, расход $Q$, условия $\mathbf{z}$", 7.7, .65, STEEL)
    columns = (
        (2, "Интегральная\nСредняя скорость,\nдлительность, проходка"),
        (6, "Дифференциальная\nНачальные условия,\nизменение состояний"),
        (10, "Комбинированная\nКривая скорости,\nпроходка и стойкость"),
    )
    for center, content in columns:
        box(ax, (center, 2.95), content, 3.72, 1.5)
        arrow(ax, (6 + (center - 6) * .55, 4.8), (center, 3.73), BLUE)
        arrow(ax, (center, 2.15), (6 + (center - 6) * .60, 1.1), BLUE)
    box(ax, (6, .68), "Допустимые варианты и расчёт критерия", 7.5, .65, STEEL)
    return fig


def badalov():
    fig, ax = sheet(145, 75)
    tau = np.linspace(0, 3, 301)
    linear = tau[tau <= 1]
    ax.plot(linear, 1 - linear, "-.", color=RUST, lw=1.6, label=r"$k=0$")
    ax.plot(tau, np.exp(-tau), "-", color=BLUE, lw=2, label=r"$k=1$")
    ax.plot(tau, 1 / (1 + tau), "--", color="#345e45", lw=1.7, label=r"$k=2$")
    ax.set(xlim=(0, 3), ylim=(0, 1.05), xlabel=r"Безразмерное время $\tau$",
           ylabel=r"Относительная скорость $V/V_0$")
    ax.grid(color="#dddfe3", linewidth=.6)
    ax.legend(frameon=False)
    return fig


def well_logging():
    fig, ax = sheet(130, 94)
    ax.set(xlim=(0, 10), ylim=(0, 7.4))
    ax.axis("off")
    box(ax, (2.42, 6.33), "Каналы ГТИ\nГлубина, время, режим", 4.5, .95, STEEL)
    box(ax, (7.58, 6.33), "Входы модели\nРежим, порода, долото", 4.5, .95, STEEL)
    arrow(ax, (2.42, 5.81), (2.42, 4.99), BLUE)
    arrow(ax, (7.58, 5.81), (7.58, 4.99), BLUE)
    box(ax, (2.42, 4.32), "Измеренная скорость\nна интервалах бурения", 4.5, 1.2)
    box(ax, (7.58, 4.32), "Прогноз скорости\nУточнить прочность, износ,\nпараметры модели", 4.5, 1.2)
    arrow(ax, (2.42, 3.65), (3.6, 2.96), BLUE)
    arrow(ax, (7.58, 3.65), (6.4, 2.96), BLUE)
    box(ax, (5, 2.36), "Согласование по глубине ствола,\nинтервалу усреднения и единицам", 7.9, 1.08)
    arrow(ax, (5, 1.76), (5, 1.15), BLUE)
    box(ax, (5, .61), "Сравнение прогноза с наблюдением", 7.9, .85, STEEL)
    return fig


def case_figures():
    inputs = read_inputs()
    results = json.loads((CALC / "RESULTS.json").read_text(encoding="utf-8"))
    cost = cost_grid(inputs, results)
    cost.set_size_inches(170 / 25.4, 100 / 25.4)
    ax = cost.axes[0]
    ax.set_title("")
    for annotation in list(ax.texts):
        annotation.remove()
    ax.legend(loc="upper right", facecolor="white", edgecolor="#cbd0d5",
              framealpha=1, fontsize=9, handlelength=1.48)
    curves = sensitivity(inputs)
    curves.set_size_inches(170 / 25.4, 79 / 25.4)
    for headline in curves.texts:
        headline.set_visible(False)
        headline.set_in_layout(False)
    curves.axes[1].legend(loc="lower right", frameon=True, fontsize=9, handlelength=2.2)
    return cost, curves


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.titlesize": 10, "svg.hashsalt": "texbur-stage4",
                         "text.color": INK, "axes.labelcolor": INK,
                         "figure.constrained_layout.h_pad": .045})
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figures = (contact(), operating_conditions(), model_types(), badalov(),
               well_logging(), *case_figures())
    for number, figure in enumerate(figures, start=1):
        path = OUTPUT / f"ris-{number}"
        figure.savefig(path.with_suffix(".png"), dpi=300, metadata={"Software": "Matplotlib"})
        vector = StringIO()
        figure.savefig(vector, format="svg", metadata={"Date": None})
        path.with_suffix(".svg").write_text(
            "\n".join(line.rstrip() for line in vector.getvalue().splitlines()) + "\n",
            encoding="utf-8")
        plt.close(figure)


if __name__ == "__main__":
    main()
