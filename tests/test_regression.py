import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from regression import build_evaluation_report, prepare_dataset, train_and_evaluate


ROOT = Path(__file__).resolve().parents[1]


class RegressionTests(unittest.TestCase):
    def test_terrain_example_fits_expected_line_and_has_twenty_records(self):
        data = pd.read_csv(ROOT / "data" / "terrenos.csv")
        result = train_and_evaluate(data, "terrenos")

        self.assertEqual(len(data), 20)
        self.assertAlmostEqual(result.slope, 500.0, places=7)
        self.assertAlmostEqual(result.intercept, 5000.0, places=7)
        self.assertAlmostEqual(result.r2, 1.0, places=7)
        self.assertAlmostEqual(result.mae, 0.0, places=7)

    def test_sales_holdout_preserves_time_order_and_fits_expected_line(self):
        data = pd.read_csv(ROOT / "data" / "ventas.csv")
        result = train_and_evaluate(data, "ventas")

        self.assertEqual(len(data), 24)
        self.assertGreater(
            result.test_features["Mes"].min(),
            result.test_features["Mes"].max() - result.test_size,
        )
        self.assertAlmostEqual(result.slope, 500.0, places=7)
        self.assertAlmostEqual(result.intercept, 2500.0, places=7)
        self.assertAlmostEqual(result.r2, 1.0, places=7)
        self.assertAlmostEqual(result.mae, 0.0, places=7)

    def test_headers_are_normalized_and_non_numeric_values_are_rejected(self):
        normalized = prepare_dataset(
            pd.DataFrame({"Área (m²)": [10, 20, 30, 40, 50], "Precio (S/)": [1, 2, 3, 4, 5]}),
            "terrenos",
        )
        self.assertEqual(list(normalized.columns), ["Area (m²)", "Precio (S/)"])

        with self.assertRaisesRegex(ValueError, "no numéricos"):
            prepare_dataset(
                pd.DataFrame({"Area": [10, 20, 30, 40, "inválido"], "Precio": [1, 2, 3, 4, 5]}),
                "terrenos",
            )

    def test_too_few_rows_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "al menos 5 registros"):
            train_and_evaluate(
                pd.DataFrame({"Area": [10, 20, 30, 40], "Precio": [1, 2, 3, 4]}),
                "terrenos",
            )

    def test_sales_rows_are_sorted_before_the_time_based_split(self):
        data = pd.DataFrame(
            {"Mes": [5, 1, 4, 2, 3], "Ventas": [5000, 1000, 4000, 2000, 3000]}
        )
        result = train_and_evaluate(data, "ventas")

        self.assertEqual(list(result.test_features["Mes"]), [4, 5])
        self.assertAlmostEqual(result.slope, 1000.0, places=7)

    def test_non_positive_area_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "mayores que cero"):
            train_and_evaluate(
                pd.DataFrame(
                    {"Area": [0, 10, 20, 30, 40], "Precio": [5, 10, 15, 20, 25]}
                ),
                "terrenos",
            )

    def test_evaluation_report_contains_predictions_and_consistent_errors(self):
        data = pd.DataFrame(
            {
                "Area": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                "Precio": [10000, 15000, 21000, 25000, 31000, 34000, 41000, 45000, 49000, 56000],
            }
        )
        result = train_and_evaluate(data, "terrenos")
        report = build_evaluation_report(result, "terrenos")

        self.assertEqual(len(report), result.test_size)
        self.assertTrue(
            {
                "Area (m²)",
                "Valor real (S/)",
                "Predicción (S/)",
                "Error (S/)",
                "Error absoluto (S/)",
            }.issubset(report.columns)
        )
        self.assertTrue(
            (report["Error (S/)"] == report["Predicción (S/)"] - report["Valor real (S/)"]).all()
        )
        self.assertTrue(
            (report["Error absoluto (S/)"] == report["Error (S/)"].abs()).all()
        )
        self.assertAlmostEqual(
            result.rmse,
            np.sqrt(np.mean(np.square(result.test_predictions - result.test_actual))),
        )


if __name__ == "__main__":
    unittest.main()
