"""Рисунки к защите ЛР №4 (оптимизация режима бурения).

Рис. 1–4 — иллюстративные (модельные числа), рис. 5–6 — пересчёт образца из пособия
(стр. 37–39), по формулам (4.1)–(4.10).
Запуск: python3 figures.py  → PNG в ../рисунки/
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "рисунки")
os.makedirs(OUT, exist_ok=True)

C1, C2, C3, C4, C5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
INK, MUTED = "#222222", "#888888"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.8,
    "lines.linewidth": 2.2, "savefig.dpi": 160, "savefig.bbox": "tight",
})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name))
    plt.close(fig)


def bisect(f, a, b, it=200):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2
        if (f(m) > 0) == (fa > 0):
            a, fa = m, f(m)
        else:
            b = m
    return (a + b) / 2


# Модель износа: v(t) = v0·e^(−a t), h(t) = v0/a·(1 − e^(−a t))
V0, A = 12.0, 0.05          # м/ч, 1/ч
TAU = 15.0                  # t_сп + t_в, ч
TAU_C = 15.0 + 10.0         # t_сп + t_в + C_д/C_в, ч


def v(t):
    return V0 * math.exp(-A * t)


def h(t):
    return V0 / A * (1 - math.exp(-A * t))


def t_opt(tau):
    # условие оптимума: v(t)·(t + τ) = h(t)
    return bisect(lambda t: v(t) * (t + tau) - h(t), 0.01, 300)


T1, T2 = t_opt(TAU), t_opt(TAU_C)


# ---------- Рис. 1. Графоаналитический метод (касательная) ----------
def fig1():
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ts = [i * 0.5 for i in range(0, 161)]
    ax.plot(ts, [h(t) for t in ts], color=INK, label="h(t) — кривая проходки")
    for tau, t0, col, lab in [(TAU, T1, C1, "max $V_р$"), (TAU_C, T2, C2, "min C")]:
        slope = h(t0) / (t0 + tau)
        xs = [-tau, t0 + 25]
        ax.plot(xs, [slope * (x + tau) for x in xs], color=col, lw=1.6, ls="--")
        ax.plot([t0], [h(t0)], "o", color=col, ms=8, zorder=5)
        ax.plot([t0, t0], [0, h(t0)], color=col, lw=1, ls=":")
        ax.annotate(f"$t_{{опт}}$ ({lab}) ≈ {t0:.0f} ч", (t0, 0), xytext=(t0 + 1.5, 8 if col == C1 else 30),
                    color=col, fontsize=10)
        ax.plot([-tau], [0], "s", color=col, ms=7, zorder=5)
    ax.annotate("", xy=(-TAU, -14), xytext=(0, -14), arrowprops=dict(arrowstyle="<->", color=C1))
    ax.text(-TAU / 2, -24, "$t_{сп}+t_в$", color=C1, ha="center")
    ax.annotate("", xy=(-TAU_C, -36), xytext=(0, -36), arrowprops=dict(arrowstyle="<->", color=C2))
    ax.text(-TAU_C / 2, -47, "$t_{сп}+t_в+C_д/C_в$", color=C2, ha="center")
    ax.axvline(0, color=INK, lw=1)
    ax.axhline(0, color=INK, lw=1)
    ax.set_xlim(-TAU_C - 3, 80)
    ax.set_ylim(-55, 240)
    ax.set_xlabel("время бурения долотом t, ч")
    ax.set_ylabel("проходка h, м")
    ax.set_title("Касательная из точки (−τ; 0) к кривой h(t): точка касания = $t_{опт}$")
    ax.legend(loc="upper left", frameon=False)
    save(fig, "рис1_графоаналитический_метод.png")


# ---------- Рис. 2. Зависимости v(t) и h(t) ----------
def fig2():
    a = 0.05
    laws = [
        ("v = const (нет износа)", lambda t: 10, lambda t: 10 * t, C1, "-"),
        ("линейная: v₀(1 − at)", lambda t: 10 * max(0, 1 - a / 1.25 * t), lambda t: 10 * (t - a / 1.25 * t * t / 2) if t <= 25 else 125, C2, "--"),
        ("экспонента: v₀e^(−at)", lambda t: 10 * math.exp(-a * t), lambda t: 10 / a * (1 - math.exp(-a * t)), C3, "-."),
        ("гипербола: v₀/(1 + at)", lambda t: 10 / (1 + a * t), lambda t: 10 / a * math.log(1 + a * t), C5, ":"),
        ("Бадалов, β = 0,5", lambda t: 10 / (1 + a * t) ** 0.5, lambda t: 10 * ((1 + a * t) ** 0.5 - 1) / (a * 0.5), C4, (0, (6, 2, 1, 2))),
    ]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    ts = [i * 0.25 for i in range(0, 161)]
    for lab, fv, fh, col, ls in laws:
        ax1.plot(ts, [fv(t) for t in ts], color=col, ls=ls, label=lab)
        ax2.plot(ts, [fh(t) for t in ts], color=col, ls=ls, label=lab)
    ax1.set_title("механическая скорость v(t)")
    ax1.set_xlabel("t, ч"); ax1.set_ylabel("v, м/ч"); ax1.set_ylim(0, 11)
    ax2.set_title("проходка h(t) = ∫v dt")
    ax2.set_xlabel("t, ч"); ax2.set_ylabel("h, м"); ax2.set_ylim(0, 260)
    fig.legend(*ax1.get_legend_handles_labels(), loc="lower center", ncol=3, frameon=False, fontsize=9.5,
               bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    save(fig, "рис2_зависимости_v_от_t.png")


# ---------- Рис. 3. Зоны разрушения v(P) ----------
def fig3():
    P1, P2, P3 = 1.0, 2.0, 3.4

    def f(p):
        if p <= P1:
            return 0.4 * p
        if p <= P2:
            return 0.4 + 0.4 * (p - P1) + 1.1 * (p - P1) ** 2
        if p <= P3:
            return 1.9 + 2.6 * (p - P2)
        return 1.9 + 2.6 * (P3 - P2) + 0.6 * (p - P3) - 0.35 * (p - P3) ** 2
    ps = [i * 0.01 for i in range(0, 451)]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(ps, [f(p) for p in ps], color=INK)
    for x in (P1, P2, P3):
        ax.axvline(x, color=MUTED, lw=1, ls="--")
    for x0, x1, txt in [(0, P1, "I\nповерхностное\n(истирание)"), (P1, P2, "II\nусталостное"),
                        (P2, P3, "III\nобъёмное"), (P3, 4.5, "IV\nухудшение\nочистки забоя")]:
        ax.text((x0 + x1) / 2, 7.7, txt, ha="center", va="top", fontsize=9.5)
    ax.axvspan(P2 + 0.15, P3 - 0.1, color=C3, alpha=0.18)
    ax.text((P2 + P3) / 2, 0.5, "рациональная\nнагрузка", ha="center", color="#0b6e4b", fontsize=9.5)
    ax.set_xticks([P1, P2, P3]); ax.set_xticklabels(["$P_1$", "$P_{кр}$ (Федоров)", "$P_3$"])
    ax.set_yticks([])
    ax.set_xlim(0, 4.5); ax.set_ylim(0, 7.9)
    ax.set_xlabel("осевая нагрузка на долото P")
    ax.set_ylabel("механическая скорость $v_м$")
    ax.set_title("Зоны разрушения породы долотом (n = const)")
    save(fig, "рис3_зоны_разрушения.png")


# ---------- Рис. 4. Аналитический метод: v(t) = Vр(t) ----------
def fig4():
    ts = [i * 0.5 for i in range(1, 161)]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.plot(ts, [v(t) for t in ts], color=INK, label="мгновенная скорость v(t)")
    ax.plot(ts, [h(t) / (t + TAU) for t in ts], color=C1, label="рейсовая $V_р(t)=h/(t+t_{сп}+t_в)$")
    vr = h(T1) / (T1 + TAU)
    ax.plot([T1], [vr], "o", color=C1, ms=8, zorder=5)
    ax.plot([T1, T1], [0, vr], color=C1, lw=1, ls=":")
    ax.annotate(f"max $V_р$ при v = $V_р$\n$t_{{опт}}$ ≈ {T1:.0f} ч", (T1, vr), xytext=(T1 + 6, vr + 2.5),
                arrowprops=dict(arrowstyle="->", color=C1), color=C1)
    ax.set_xlabel("время бурения долотом t, ч"); ax.set_ylabel("скорость, м/ч")
    ax.set_ylim(0, 12.5); ax.set_xlim(0, 80)
    ax.set_title("Условие оптимума: $dV_р/dt = 0$  ⇔  $v(t) = V_р(t)$")
    ax.legend(frameon=False, loc="upper right")
    save(fig, "рис4_аналитический_метод.png")


# ---------- Рис. 5–6. Образец ЛР (пособие, стр. 37–39), скважина №1 ----------
CV, CD, TSP, TV = 11054, 106500, 29.1, 0.9
HD = [144, 155, 146, 154, 151]
TB = [30, 25, 21, 26, 19]
PMIN, PMAX, NMIN, NMAX = 130000, 220000, 40, 80
P0, N0 = 150000, 60


def lab_model():
    hd, tb = sum(HD) / len(HD), sum(TB) / len(TB)
    vm = hd / tb
    k = vm / (N0 ** 0.8 * P0 ** 1.4)
    a = tb * N0 ** 0.7 * P0 ** 1.2
    B, D, M = CV / k, CV * (TSP + TV) / (k * a), CD / (k * a)
    return lambda n, P: B / (n ** 0.8 * P ** 1.4) + (D + M) / (n ** 0.1 * P ** 0.2)


def n_lim(P):
    return (NMIN - NMAX) / (PMAX - PMIN) * (P - PMIN) + NMAX


def fig5():
    C = lab_model()
    loads = [130000, 150000, 170000, 190000, 200000]
    cols = [C1, C2, C3, C4, C5]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    best = None
    for P, col in zip(loads, cols):
        ns = [n for n in range(40, 81, 5) if n <= n_lim(P) + 0.5]
        cs = [C(n, P) for n in ns]
        ax.plot(ns, cs, "o-", color=col, ms=5, lw=1.8, label=f"P = {P // 1000} кН")
        for n, c in zip(ns, cs):
            if best is None or c < best[2]:
                best = (n, P, c)
    n, P, c = best
    ax.annotate(f"min C ≈ {c:.0f} руб/м\nP = {P // 1000} кН, n = {n} об/мин", (n, c), xytext=(n + 6, 4080),
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_xlabel("частота вращения n, об/мин"); ax.set_ylabel("C, руб/м")
    ax.set_title("Затраты на 1 м проходки C(n) при разных P (образец ЛР, скв. №1)")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_ylim(4000, 6400)
    save(fig, "рис5_затраты_C_от_n_и_P.png")


def fig6():
    fig, ax = plt.subplots(figsize=(7, 4.6))
    ps = [PMIN, PMAX]
    ax.fill_between([p / 1000 for p in ps], [NMIN, NMIN], [n_lim(p) for p in ps], color=C1, alpha=0.15)
    ax.plot([p / 1000 for p in ps], [n_lim(p) for p in ps], color=C1, label="граница (4.10): $n_д$ ≤ $n(P_д)$")
    ax.text(150, 47, "допустимая\nобласть режимов", color="#1c5cab", fontsize=10)
    ax.plot([190], [50], "o", color=C2, ms=9, zorder=5)
    ax.annotate("оптимум — у границы\n(узел сетки 190 кН; 50)", (190, 50), xytext=(186, 68), arrowprops=dict(arrowstyle="->", color=C2), color=C2)
    ax.annotate("($P_{min}$; $n_{max}$)", (130, 80), xytext=(132, 81.5), fontsize=9)
    ax.annotate("($P_{max}$; $n_{min}$)", (220, 40), xytext=(196, 37), fontsize=9)
    ax.set_xlim(120, 230); ax.set_ylim(34, 86)
    ax.set_xlabel("осевая нагрузка $P_д$, кН"); ax.set_ylabel("$n_д$, об/мин")
    ax.set_title("Паспортное ограничение «нагрузка — частота» (215,9 СЗ-ГАУ)")
    ax.legend(frameon=False, loc="upper right")
    save(fig, "рис6_область_допустимых_режимов.png")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6):
        f()
    print(f"t_опт (max Vр) = {T1:.1f} ч, t_опт (min C) = {T2:.1f} ч")
