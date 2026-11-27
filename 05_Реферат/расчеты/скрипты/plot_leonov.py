"""Generate the Leonov sensitivity and published-grid figures from the stage 2 data."""

import argparse
from fractions import Fraction
from io import StringIO
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from leonov import CALC_DIR, Leonov, n_boundary, read_inputs


def sensitivity(inputs):
    model = Leonov.calibrate(inputs)
    limits = inputs["limits"]
    n_cap = n_boundary(model.P0, limits)
    # Solve the same linear boundary for P at n0.
    P_cap = limits["P_min_N"] + (
        Fraction(limits["n_max_rpm"] - model.n0, limits["n_max_rpm"] - limits["n_min_rpm"])
        * (limits["P_max_N"] - limits["P_min_N"])
    )
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.7), sharey=True, layout="constrained")
    series = {
        "V_m_per_h": (model.V_star, r"$\overline{V}_m/V_*$", "#0072b2", "-"),
        "t_h": (model.t_star, r"$t/t_*$", "#bf4c04", "--"),
        "H_m": (model.H_star, r"$H/H_*$", "#007e62", "-."),
    }
    panels = (
        (axes[0], "Нагрузка при 60 об/мин", "Осевая нагрузка, кН", model.P0 / 1000,
         limits["P_min_N"], float(P_cap), 1000, lambda value: model.normalized(value, model.n0)),
        (axes[1], "Частота при 150 кН", "Частота вращения, об/мин", model.n0,
         limits["n_min_rpm"], float(n_cap), 1, lambda value: model.normalized(model.P0, value)),
    )
    for ax, title, label, reference, low, high, scale, evaluate in panels:
        values = [low + i * (high - low) / 200 for i in range(201)]
        outputs = [evaluate(value) for value in values]
        for key, (baseline, legend, color, linestyle) in series.items():
            ax.plot([value / scale for value in values],
                    [result[key] / baseline for result in outputs],
                    label=legend, color=color, linestyle=linestyle, linewidth=2)
        ax.axhline(1, color="#9aa5b1", linewidth=0.7, zorder=0)
        ax.axvline(reference, color="#64748b", linewidth=1, linestyle=":", zorder=0)
        ax.plot(reference, 1, "o", color="#25364a", markersize=4)
        ax.set(title=title, xlabel=label)
        ax.grid(axis="y", color="#e4e9ef", linewidth=0.7)
    axes[0].set_ylabel("Отношение к опорному режиму")
    axes[1].legend(loc="best", frameon=False)
    figure.suptitle("Чувствительность показателей по модели Леонова",
                    fontsize=15, fontweight="bold")
    return figure


def cost_grid(inputs, results):
    lim = inputs["limits"]
    nodes = results["nodes"]
    reference = results["reference_node"]
    optimum = results["minimum_cost_node"]
    probes = results["diagnostic_probes"]
    costs = [node["original"]["C_rub_per_m"] for node in nodes]

    figure, ax = plt.subplots(figsize=(10.2, 6.1), layout="constrained")
    min_P, max_P = lim["P_min_N"] / 1000, lim["P_max_N"] / 1000
    min_n, max_n = lim["n_min_rpm"], lim["n_max_rpm"]
    ax.fill_between([min_P, max_P], [min_n, min_n], [max_n, min_n], color="#ebf4f5")
    ax.plot([min_P, max_P], [max_n, min_n], color="#3e5965", linestyle="--",
            label="Точная граница (4.10)")
    ax.vlines(min_P, min_n, max_n, color="#9aaab6", linewidth=1)
    ax.hlines(min_n, min_P, max_P, color="#9aaab6", linewidth=1)
    scatter = ax.scatter([node["P_kN"] for node in nodes], [node["n_rpm"] for node in nodes],
                         c=costs, cmap="viridis", s=77, edgecolors="#162a32", linewidths=0.65,
                         zorder=3, label="26 узлов с. 38")
    figure.colorbar(scatter, ax=ax, label="Расчётная стоимость, руб./м")
    ax.scatter(reference["P_kN"], reference["n_rpm"], s=175, facecolors="none",
               edgecolors="#283647", linewidths=1.5, marker="s", zorder=4, label="Опорный режим")
    ax.scatter(optimum["P_kN"], optimum["n_rpm"], s=205, facecolors="none",
               edgecolors="#bc4200", linewidths=2.0, zorder=5, label="Минимум на сетке")
    continuous = probes["at_continuous_boundary"]
    excluded = probes["excluded_counterfactual"]
    ax.scatter(continuous["P_kN"], continuous["n_rpm"], s=71, color="#1a5b88",
               marker="D", zorder=5, label="Граница при 190 кН")
    ax.scatter(excluded["P_kN"], excluded["n_rpm"], s=73, color="#8d2434",
               marker="x", linewidths=2, zorder=5, label="Недопустимый режим")

    minimum_cost = results["grid_extrema"]["C_rub_per_m"]["value"]
    cost_label = f"{minimum_cost:,.2f}".translate(str.maketrans({",": " ", ".": ","}))
    annotations = (
        (optimum, f"{cost_label} руб./м", (204, 42.4), "#8e3200"),
        (continuous, "53⅓ об/мин", (176, 56.7), "#1a5b88"),
        (excluded, "200 кН / 50 об/мин", (205, 54.7), "#8d2434"),
    )
    for point, label, label_at, color in annotations:
        ax.annotate(label, (point["P_kN"], point["n_rpm"]), xytext=label_at, color=color,
                    fontsize=9, arrowprops={"arrowstyle": "-", "color": color},
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.92})
    ax.set(xlim=(125, 229), ylim=(37, 84), xlabel="Осевая нагрузка, кН",
           ylabel="Частота вращения, об/мин",
           xticks=[130, 150, 170, 190, 200, 220], yticks=inputs["printed_grid"]["n_rpm"])
    ax.set_axisbelow(True)
    ax.grid(color="#e1e6ec", linewidth=0.65)
    ax.legend(loc="upper right", facecolor="white", edgecolor="#dce3eb", framealpha=1, fontsize=9)
    ax.set_title("Стоимость метра на опубликованной сетке", fontsize=15, fontweight="bold")
    return figure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=CALC_DIR / "RESULTS.json")
    parser.add_argument("--output-dir", type=Path, default=CALC_DIR / "графики")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    inputs = read_inputs()
    results = json.loads(args.results.read_text(encoding="utf-8"))
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.hashsalt": "leonov-2007-stage2"})
    for name, figure in (("sensitivity", sensitivity(inputs)), ("cost_grid", cost_grid(inputs, results))):
        figure.savefig(args.output_dir / f"{name}.png", dpi=180)
        svg = StringIO()
        figure.savefig(svg, format="svg", metadata={"Date": None})
        # Matplotlib adds trailing spaces inside path data. Line breaks still delimit commands.
        svg_text = "\n".join(line.rstrip() for line in svg.getvalue().splitlines()) + "\n"
        (args.output_dir / f"{name}.svg").write_text(svg_text, encoding="utf-8")
        plt.close(figure)


if __name__ == "__main__":
    main()
