"""Regression tests for the source transcription, equations and generated results."""

from decimal import Decimal, localcontext
from fractions import Fraction
from hashlib import sha256
import json
import unittest

from leonov import CALC_DIR, Leonov, admissible, calculate, display_round, n_boundary, read_inputs


def reference_decimal(P_N, n_rpm):
    """Separate 50-digit calculation using the orchestrator's relative equations."""
    with localcontext() as context:
        context.prec = 50
        x = Decimal(P_N) / 150000
        n = Fraction(n_rpm)
        y = Decimal(n.numerator) / (60 * n.denominator)
        V = Decimal(750) / 121 * x**Decimal("1.4") * y**Decimal("0.8")
        t = Decimal(121) / 5 * x**Decimal("-1.2") * y**Decimal("-0.7")
        H = V * t
        T = t + 30
        return {
            "V_m_per_h": V, "t_h": t, "H_m": H, "T_h": T, "V_r_m_per_h": H / T,
            "C_rub_per_m": (106500 + 11054 * T) / H,
        }


class LeonovTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = read_inputs()
        cls.model = Leonov.calibrate(cls.inputs)
        cls.results = calculate(cls.inputs)

    def test_source_transcription_and_units(self):
        self.assertEqual(self.inputs["units"]["P_N"], "Н")
        self.assertEqual(self.inputs["units"]["n_rpm"], "об/мин")
        self.assertEqual(self.inputs["units"]["C_rub_per_m"], "руб./м")
        self.assertEqual(self.inputs["reference"], {"P_N": 150000, "n_rpm": 60})
        self.assertEqual(self.inputs["limits"], dict(
            P_min_N=130000, P_max_N=220000, n_min_rpm=40, n_max_rpm=80,
        ))
        self.assertEqual(self.inputs["economics"], dict(
            C_b_rub=106500, C_h_rub_per_h=11054, t_sp_h=29.1, t_aux_h=0.9,
        ))
        self.assertEqual(self.inputs["exponents"], dict(p_v=1.4, q_v=0.8, p_t=1.2, q_t=0.7))
        self.assertEqual([(r["H_m"], r["t_h"]) for r in self.inputs["runs"]],
                         [(144, 30), (155, 25), (146, 21), (154, 26), (151, 19)])
        repository = CALC_DIR.parents[1]
        for name in ("manual", "lecture"):
            with self.subTest(source=name):
                source = self.inputs["sources"][name]
                self.assertEqual(
                    sha256((repository / source["path_from_repository_root"]).read_bytes()).hexdigest(),
                    source["sha256"],
                )

    def test_reference_calibration(self):
        self.assertEqual((self.model.V_star, self.model.t_star, self.model.H_star), (750/121, 24.2, 150))
        self.assertEqual(self.model.overhead, 30)
        self.assertAlmostEqual(self.model.k / 1.3280888484884685e-8, 1, places=13)
        self.assertAlmostEqual(self.model.A / 691561411.6215498, 1, places=13)
        self.assertAlmostEqual(self.results["comparison"]["C_rub_per_m"]["reference"],
                               4704.1786666667, places=8)

    def test_grid_transcription_and_eligibility(self):
        grid = self.inputs["printed_grid"]
        self.assertEqual(grid["n_rpm"], list(range(40, 81, 5)))
        self.assertEqual([row["P_N"] for row in grid["rows"]], [130000, 150000, 170000, 190000, 200000])
        # Tenths transcribed from C36:K40 on p. 38. Blanks start after each listed value.
        printed_tenths = [
            [61439, 58362, 55821, 53680, 51846, 50255, 48859, 47621, 46514],
            [55084, 52510, 50380, 48583, 47042, 45703, 44526],
            [50367, 48158, 46328, 44782, 43454],
            [46730, 44797, 43193],
            [45206, 43387],
        ]
        for row, expected in zip(grid["rows"], printed_tenths, strict=True):
            with self.subTest(P_N=row["P_N"]):
                self.assertEqual(row["C_rub_per_m"],
                                 [x / 10 for x in expected] + [None] * (9 - len(expected)))
                # (4.10) rewritten as an integer inequality for the 45 candidate pairs.
                admitted = [n for n in grid["n_rpm"] if 9 * (80 - n) >= 4 * (row["P_N"] // 1000 - 130)]
                self.assertEqual(admitted, grid["n_rpm"][:len(expected)])
        self.assertEqual(self.results["node_count"], 26)
        self.assertEqual(len({(row["P_N"], row["n_rpm"]) for row in self.results["nodes"]}), 26)

    def test_exact_boundary_and_rounding(self):
        limits = self.inputs["limits"]
        expected = ["80", "640/9", "560/9", "160/3", "440/9"]
        for row, exact in zip(self.results["row_boundaries"], expected, strict=True):
            with self.subTest(P_N=row["P_N"]):
                P, cap = row["P_N"], Fraction(exact)
                self.assertEqual(n_boundary(P, limits), cap)
                self.assertTrue(admissible(P, cap, limits))
                self.assertFalse(admissible(P, cap + Fraction(1, 10**10), limits))
                self.assertEqual(int(display_round(float(cap), "1")), row["printed_n_limit_rpm"])
        self.assertTrue(admissible(220000, 40, limits))
        self.assertFalse(admissible(129999, 40, limits))
        self.assertFalse(admissible(220001, 40, limits))
        self.assertFalse(admissible(130000, 39, limits))
        self.assertFalse(admissible(200000, 49, limits))
        self.assertFalse(admissible(200000, 50, limits))
        self.assertFalse(admissible(200, 50, limits))
        self.assertEqual(display_round(12.25), Decimal("12.3"))

    def test_equivalence_on_all_nodes(self):
        for node in self.results["nodes"]:
            P, n = node["P_N"], node["n_rpm"]
            with self.subTest(P_N=P, n_rpm=n):
                independent = reference_decimal(P, n)
                for metric, expected in independent.items():
                    self.assertAlmostEqual(node["original"][metric], float(expected), places=9)
                    self.assertAlmostEqual(node["normalized"][metric], float(expected), places=9)
                cost_identity = self.model.C_h / node["original"]["V_r_m_per_h"]
                cost_identity += self.model.C_b / node["original"]["H_m"]
                self.assertAlmostEqual(node["C_BDM_rub_per_m"], cost_identity, places=9)
                self.assertAlmostEqual(node["C_BDM_rub_per_m"], float(independent["C_rub_per_m"]), places=9)

    def test_grid_extrema(self):
        optimum = self.results["minimum_cost_node"]
        self.assertEqual((optimum["P_N"], optimum["n_rpm"]), (190000, 50))
        for metric, expected in (
            ("V_m_per_h", 7.4586147363), ("t_h", 20.7036743477), ("H_m", 154.4207305858),
            ("T_h", 50.7036743477), ("V_r_m_per_h", 3.0455530604), ("C_rub_per_m", 4319.2284721744),
        ):
            with self.subTest(metric=metric):
                entry = self.results["grid_extrema"][metric]
                self.assertEqual(entry["nodes"], [optimum])
                self.assertAlmostEqual(entry["value"], expected, places=8)

    def test_all_printed_residuals_and_D_diagnostic(self):
        regression = self.results["regression"]
        self.assertEqual(regression["threshold_rub_per_m"], 0.12)
        self.assertAlmostEqual(self.results["calibration"]["D"], 36106.2872352185, places=8)
        self.assertEqual(regression["printed_D_only"]["D"], 36106.83)
        for node in self.results["nodes"]:
            expected = reference_decimal(node["P_N"], node["n_rpm"])["C_rub_per_m"]
            printed = Decimal(str(node["C_printed_rub_per_m"]))
            residual = float(expected - printed)
            self.assertAlmostEqual(node["residual_rub_per_m"], residual, places=9)
            self.assertLessEqual(abs(residual), regression["threshold_rub_per_m"])
            self.assertEqual(node["C_display_rub_per_m"], float(display_round(expected)))
        main, diagnostic = regression["main"], regression["printed_D_only"]
        self.assertEqual(main["node_at_maximum"], {"P_N": 130000, "P_kN": 130, "n_rpm": 70})
        self.assertAlmostEqual(main["maximum_absolute_rub_per_m"], 0.111011894, places=8)
        self.assertAlmostEqual(diagnostic["maximum_absolute_rub_per_m"], 0.077336461, places=8)
        self.assertEqual((main["rounded_matches"], diagnostic["rounded_matches"]), (13, 20))

    def test_boundary_probes(self):
        probes = self.results["diagnostic_probes"]
        continuous = probes["at_continuous_boundary"]
        excluded = probes["excluded_counterfactual"]
        self.assertTrue(continuous["eligible_by_exact_boundary"])
        self.assertFalse(excluded["eligible_by_exact_boundary"])
        self.assertFalse(continuous["in_printed_cost_cells"])
        self.assertFalse(excluded["in_printed_cost_cells"])
        for probe, expected in ((continuous, 4226.3993037440), (excluded, 4187.5764483326)):
            cost = probe["metrics"]["C_rub_per_m"]
            self.assertAlmostEqual(cost, expected, places=8)
            self.assertAlmostEqual(cost, float(reference_decimal(
                probe["P_N"], Fraction(probe["n_exact"]))["C_rub_per_m"]), places=9)
            self.assertLess(cost, self.results["grid_extrema"]["C_rub_per_m"]["value"])

    def test_committed_results_match_calculation(self):
        recorded = json.loads((CALC_DIR / "RESULTS.json").read_text(encoding="utf-8"))
        self.assertEqual(recorded, self.results)


if __name__ == "__main__":
    unittest.main()
