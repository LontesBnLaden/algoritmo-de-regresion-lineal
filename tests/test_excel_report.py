import unittest
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd

from excel_report import create_excel_report
from regression import build_evaluation_report, prepare_dataset, train_and_evaluate


ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


class ExcelReportTests(unittest.TestCase):
    def build_report(self, case_name: str) -> bytes:
        data = prepare_dataset(
            pd.read_csv(ROOT / "data" / f"{case_name}.csv"), case_name
        )
        result = train_and_evaluate(data, case_name)
        evaluation = build_evaluation_report(result, case_name)
        prediction_value = float(data.iloc[-1, 0])
        prediction_amount = float(
            result.model.predict(
                pd.DataFrame({data.columns[0]: [prediction_value]})
            )[0]
        )
        future = None
        if case_name == "ventas":
            future_months = np.arange(
                int(data.iloc[:, 0].max()) + 1,
                int(data.iloc[:, 0].max()) + 7,
            )
            future = pd.DataFrame(
                {
                    "Mes": future_months,
                    "Ventas (S/)": result.model.predict(
                        pd.DataFrame({"Mes": future_months})
                    ),
                }
            )

        return create_excel_report(
            data=data,
            case_name=case_name,
            result=result,
            evaluation_report=evaluation,
            prediction=(prediction_value, prediction_amount),
            future_data=future,
        )

    def test_sales_workbook_has_executive_summary_tables_and_charts(self):
        report = self.build_report("ventas")

        with zipfile.ZipFile(BytesIO(report)) as workbook:
            workbook_xml = ET.fromstring(workbook.read("xl/workbook.xml"))
            sheet_names = [
                sheet.attrib["name"]
                for sheet in workbook_xml.findall("main:sheets/main:sheet", NAMESPACE)
            ]
            chart_files = [
                name
                for name in workbook.namelist()
                if name.startswith("xl/charts/chart") and name.endswith(".xml")
            ]

        self.assertEqual(
            sheet_names,
            ["Resumen", "Datos", "Evaluación", "Proyección"],
        )
        self.assertEqual(len(chart_files), 2)
        self.assertGreater(len(report), 10_000)

    def test_terrain_workbook_includes_scenario_sheet(self):
        report = self.build_report("terrenos")

        with zipfile.ZipFile(BytesIO(report)) as workbook:
            workbook_xml = ET.fromstring(workbook.read("xl/workbook.xml"))
            sheet_names = [
                sheet.attrib["name"]
                for sheet in workbook_xml.findall("main:sheets/main:sheet", NAMESPACE)
            ]

        self.assertEqual(sheet_names[-1], "Proyección")
        self.assertIn("xl/worksheets/sheet4.xml", workbook.namelist())


if __name__ == "__main__":
    unittest.main()
