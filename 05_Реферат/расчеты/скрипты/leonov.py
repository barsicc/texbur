"""Calculate the published Leonov grid in N and rpm, using Python 3.10+."""

import argparse
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
import json
from pathlib import Path

CALC_DIR = Path(__file__).resolve().parents[1]


def read_inputs(path=CALC_DIR / "ИСХОДНЫЕ_ДАННЫЕ.json"):
    return json.loads(path.read_text(encoding="utf-8"))


def display_round(value, quantum="0.1"):
    return Decimal(str(value)).quantize(Decimal(quantum), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Leonov:
    P0: int
    n0: int
    V_star: float
    t_star: float
    H_star: float
    p_v: float
    q_v: float
    p_t: float
    q_t: float
    C_b: float
    C_h: float
    overhead: float

    @classmethod
    def calibrate(cls, inputs):
        total_H = sum(run["H_m"] for run in inputs["runs"])
        total_t = sum(run["t_h"] for run in inputs["runs"])
        count = len(inputs["runs"])
        reference = inputs["reference"]
        costs = inputs["economics"]
        return cls(
            reference["P_N"], reference["n_rpm"],
            total_H / total_t, total_t / count, total_H / count,
            **inputs["exponents"], C_b=costs["C_b_rub"], C_h=costs["C_h_rub_per_h"],
            overhead=costs["t_sp_h"] + costs["t_aux_h"],
        )

    @property
    def k(self):
        return self.V_star / (self.P0**self.p_v * self.n0**self.q_v)

    @property
    def A(self):
        return self.t_star * self.P0**self.p_t * self.n0**self.q_t

    def cost_coefficients(self):
        return {
            "B": self.C_h / self.k,
            "D": self.C_h * self.overhead / (self.k * self.A),
            "M": self.C_b / (self.k * self.A),
        }

    def metrics(self, V, t, H):
        T = t + self.overhead
        return {
            "V_m_per_h": V, "t_h": t, "H_m": H, "T_h": T,
            "V_r_m_per_h": H / T, "C_rub_per_m": (self.C_b + self.C_h * T) / H,
        }

    def original(self, P, n):
        V = self.k * P**self.p_v * n**self.q_v
        t = self.A / (P**self.p_t * n**self.q_t)
        return self.metrics(V, t, V * t)

    def normalized(self, P, n):
        x, y = P / self.P0, n / self.n0
        V = self.V_star * x**self.p_v * y**self.q_v
        t = self.t_star * x**(-self.p_t) * y**(-self.q_t)
        H = self.H_star * x**(self.p_v - self.p_t) * y**(self.q_v - self.q_t)
        return self.metrics(V, t, H)

    def cost_expanded(self, P, n, coefficients):
        B, D, M = (coefficients[key] for key in ("B", "D", "M"))
        return (
            B / (P**self.p_v * n**self.q_v)
            + (D + M) / (P**(self.p_v - self.p_t) * n**(self.q_v - self.q_t))
        )


def n_boundary(P_N, limits):
    """Equation (4.10), evaluated exactly for integer or rational loads."""
    fraction = Fraction(P_N - limits["P_min_N"]) / (limits["P_max_N"] - limits["P_min_N"])
    return limits["n_max_rpm"] + fraction * (limits["n_min_rpm"] - limits["n_max_rpm"])


def admissible(P_N, n_rpm, limits):
    return (
        limits["P_min_N"] <= P_N <= limits["P_max_N"]
        and limits["n_min_rpm"] <= n_rpm <= n_boundary(P_N, limits)
    )


def evaluate_grid(inputs, model, coefficients):
    grid = inputs["printed_grid"]
    limits = inputs["limits"]
    diagnostic = {**coefficients, "D": inputs["diagnostics"]["printed_D"]}
    nodes, boundaries = [], []
    for row in grid["rows"]:
        P = row["P_N"]
        cap = n_boundary(P, limits)
        boundaries.append({
            "P_N": P, "P_kN": P / 1000, "n_limit_exact": str(cap),
            "n_limit_rpm": float(cap), "printed_n_limit_rpm": row["printed_n_limit_rpm"],
        })
        for n, printed in zip(grid["n_rpm"], row["C_rub_per_m"], strict=True):
            if admissible(P, n, limits) != (printed is not None):
                raise ValueError(f"Published grid and exact boundary disagree at {P} N / {n} rpm")
            if printed is None:
                continue
            original = model.original(P, n)
            cost = original["C_rub_per_m"]
            diagnostic_cost = model.cost_expanded(P, n, diagnostic)
            nodes.append({
                "P_N": P, "P_kN": P / 1000, "n_rpm": n,
                "original": original,
                "normalized": model.normalized(P, n),
                "C_BDM_rub_per_m": model.cost_expanded(P, n, coefficients),
                "C_printed_rub_per_m": printed,
                "residual_rub_per_m": cost - printed,
                "C_display_rub_per_m": float(display_round(cost)),
                "C_printed_D_rub_per_m": diagnostic_cost,
                "residual_printed_D_rub_per_m": diagnostic_cost - printed,
                "C_printed_D_display_rub_per_m": float(display_round(diagnostic_cost)),
            })
    return nodes, boundaries


def coordinates(node):
    return {key: node[key] for key in ("P_N", "P_kN", "n_rpm")}


def residual_summary(nodes, residual_key, display_key):
    worst = max(nodes, key=lambda node: abs(node[residual_key]))
    return {
        "maximum_absolute_rub_per_m": abs(worst[residual_key]),
        "signed_at_maximum_rub_per_m": worst[residual_key],
        "node_at_maximum": coordinates(worst),
        "rounded_matches": sum(node[display_key] == node["C_printed_rub_per_m"] for node in nodes),
    }


def calculate(inputs):
    model = Leonov.calibrate(inputs)
    coefficients = model.cost_coefficients()
    nodes, boundaries = evaluate_grid(inputs, model, coefficients)

    metric_directions = {
        "V_m_per_h": max, "t_h": min, "H_m": max, "T_h": min,
        "V_r_m_per_h": max, "C_rub_per_m": min,
    }
    extrema = {}
    for metric, choose in metric_directions.items():
        value = choose(node["original"][metric] for node in nodes)
        extrema[metric] = {
            "direction": choose.__name__,
            "value": value,
            "nodes": [coordinates(node) for node in nodes if node["original"][metric] == value],
        }

    optimum = min(nodes, key=lambda node: node["original"]["C_rub_per_m"])
    reference = next(node for node in nodes if (node["P_N"], node["n_rpm"]) == (model.P0, model.n0))
    comparison = {}
    for metric, baseline in reference["original"].items():
        selected = optimum["original"][metric]
        comparison[metric] = {
            "reference": baseline, "grid_minimum_cost": selected,
            "difference": selected - baseline, "change_pct": (selected - baseline) / baseline * 100,
        }

    limits = inputs["limits"]
    controls = inputs["diagnostics"]
    boundary_P = controls["boundary_probe_P_N"]
    boundary_n = n_boundary(boundary_P, limits)
    excluded_P = controls["excluded_probe"]["P_N"]
    excluded_n = controls["excluded_probe"]["n_rpm"]
    probes = {}
    for key, P, n in (
        ("at_continuous_boundary", boundary_P, boundary_n),
        ("excluded_counterfactual", excluded_P, Fraction(excluded_n)),
    ):
        probes[key] = {
            "P_N": P, "P_kN": P / 1000, "n_rpm": float(n), "n_exact": str(n),
            "n_limit_exact": str(n_boundary(P, limits)),
            "eligible_by_exact_boundary": admissible(P, n, limits),
            "in_printed_cost_cells": any((P, n) == (node["P_N"], node["n_rpm"]) for node in nodes),
            "metrics": model.normalized(P, float(n)),
        }
    return {
        "case": inputs["case"],
        "data_status": inputs["data_status"],
        "units": inputs["units"],
        "calibration": {
            "P0_N": model.P0, "n0_rpm": model.n0, "V_star_m_per_h": model.V_star,
            "t_star_h": model.t_star, "H_star_m": model.H_star, "overhead_h": model.overhead,
            "k": model.k, "A": model.A, **coefficients,
            "exponents": inputs["exponents"],
        },
        "row_boundaries": boundaries,
        "node_count": len(nodes), "nodes": nodes, "grid_extrema": extrema,
        "minimum_cost_node": coordinates(optimum),
        "reference_node": coordinates(reference),
        "comparison": comparison,
        "regression": {
            "threshold_rub_per_m": controls["printed_table_regression_threshold_rub_per_m"],
            "residual_definition": "Расчёт минус печатное значение, до округления",
            "main": residual_summary(nodes, "residual_rub_per_m", "C_display_rub_per_m"),
            "printed_D_only": {
                "D": controls["printed_D"],
                **residual_summary(nodes, "residual_printed_D_rub_per_m", "C_printed_D_display_rub_per_m"),
            },
        },
        "diagnostic_probes": probes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=CALC_DIR / "RESULTS.json")
    args = parser.parse_args()
    results = calculate(read_inputs())
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")


if __name__ == "__main__":
    main()
