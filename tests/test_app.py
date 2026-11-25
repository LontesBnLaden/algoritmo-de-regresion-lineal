import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    def test_sales_screen_renders_six_future_months(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        app.radio[0].set_value("Ventas mensuales")
        app.run()

        self.assertFalse(app.exception)
        metric_labels = {item.label for item in app.metric}
        self.assertTrue(
            {
                "R² de prueba",
                "MAE de prueba",
                "RMSE de prueba",
                "Registros analizados",
            }.issubset(metric_labels)
        )
        self.assertTrue(
            any("Diagnóstico visual del modelo" in item.value for item in app.markdown)
        )
        self.assertTrue(
            any("Historial listo: 24 registros" in item.value for item in app.success)
        )
        self.assertTrue(
            any(
                "Proyección de los próximos 6 meses" in item.value
                for item in app.markdown
            )
        )
        self.assertTrue(
            any(
                "Descargar evaluación detallada (CSV)" in item.label
                for item in app.get("download_button")
            )
        )
        forecast = app.dataframe[0].value
        self.assertEqual(len(forecast), 6)
        self.assertEqual(forecast["Mes futuro"].iloc[0], 25)
        self.assertAlmostEqual(forecast["Ventas estimadas (S/)"].sum(), 97500.0)


if __name__ == "__main__":
    unittest.main()
