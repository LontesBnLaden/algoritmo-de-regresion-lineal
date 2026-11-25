"""Create a presentation-ready Excel report for the regression dashboard."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
import xlsxwriter

from regression import CASE_SPECS, RegressionResult


NAVY = "#142B45"
TEAL = "#087F8C"
CYAN = "#28AFA7"
ORANGE = "#E88943"
INK = "#26384A"
MUTED = "#65788A"
PALE = "#F2F6F9"
WHITE = "#FFFFFF"
BORDER = "#DCE5EC"
CURRENCY_FORMAT = '"S/ " #,##0.00;[Red]-"S/ " #,##0.00'


def _python_rows(frame: pd.DataFrame) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for row in frame.itertuples(index=False, name=None):
        rows.append(
            [
                None
                if pd.isna(value)
                else value.item()
                if hasattr(value, "item")
                else value
                for value in row
            ]
        )
    return rows


def _table_sheet(
    workbook: xlsxwriter.Workbook,
    sheet_name: str,
    table_name: str,
    title: str,
    subtitle: str,
    frame: pd.DataFrame,
    formats: dict[str, xlsxwriter.format.Format],
    column_widths: list[int],
    column_formats: dict[str, xlsxwriter.format.Format] | None = None,
) -> tuple[xlsxwriter.worksheet.Worksheet, int]:
    worksheet = workbook.add_worksheet(sheet_name)
    worksheet.hide_gridlines(2)
    worksheet.set_tab_color(TEAL)
    worksheet.set_row(0, 30)
    worksheet.set_row(1, 25)
    worksheet.merge_range(
        0, 0, 0, len(frame.columns) - 1, title, formats["sheet_title"]
    )
    worksheet.merge_range(
        1, 0, 1, len(frame.columns) - 1, subtitle, formats["sheet_subtitle"]
    )

    column_formats = column_formats or {}
    columns = []
    for name in frame.columns:
        column: dict[str, Any] = {"header": name}
        if name in column_formats:
            column["format"] = column_formats[name]
        columns.append(column)

    header_row = 3
    worksheet.add_table(
        header_row,
        0,
        header_row + len(frame),
        len(frame.columns) - 1,
        {
            "name": table_name,
            "style": "Table Style Medium 2",
            "columns": columns,
            "data": _python_rows(frame),
        },
    )
    for index, name in enumerate(frame.columns):
        worksheet.set_column(
            index, index, column_widths[index], column_formats.get(name)
        )
    worksheet.freeze_panes(header_row + 1, 0)
    worksheet.set_landscape()
    worksheet.fit_to_pages(1, 0)
    worksheet.repeat_rows(header_row)
    worksheet.set_header("&LRegresión Lab&CInforme académico&R&Página &P")
    worksheet.set_footer("&LGenerado automáticamente&R&P de &N")
    worksheet.set_margins(0.35, 0.35, 0.55, 0.55)
    return worksheet, header_row + 1


def _create_formats(workbook: xlsxwriter.Workbook) -> dict[str, Any]:
    return {
        "title": workbook.add_format(
            {
                "bold": True,
                "font_name": "Aptos Display",
                "font_size": 24,
                "font_color": WHITE,
                "bg_color": NAVY,
                "valign": "vcenter",
                "align": "left",
                "text_wrap": True,
            }
        ),
        "subtitle": workbook.add_format(
            {
                "font_size": 11,
                "font_color": "#D8E7F0",
                "bg_color": NAVY,
                "valign": "vcenter",
                "text_wrap": True,
            }
        ),
        "sheet_title": workbook.add_format(
            {
                "bold": True,
                "font_size": 16,
                "font_color": WHITE,
                "bg_color": NAVY,
                "valign": "vcenter",
            }
        ),
        "sheet_subtitle": workbook.add_format(
            {
                "font_size": 10,
                "font_color": MUTED,
                "bg_color": PALE,
                "valign": "vcenter",
                "text_wrap": True,
            }
        ),
        "section": workbook.add_format(
            {
                "bold": True,
                "font_size": 11,
                "font_color": WHITE,
                "bg_color": TEAL,
                "valign": "vcenter",
            }
        ),
        "card_label": workbook.add_format(
            {
                "bold": True,
                "font_size": 9,
                "font_color": "#DCE8F1",
                "bg_color": NAVY,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
                "border": 1,
                "border_color": WHITE,
            }
        ),
        "card_value": workbook.add_format(
            {
                "bold": True,
                "font_size": 18,
                "font_color": INK,
                "bg_color": PALE,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": WHITE,
            }
        ),
        "card_currency": workbook.add_format(
            {
                "bold": True,
                "font_size": 16,
                "font_color": INK,
                "bg_color": PALE,
                "align": "center",
                "valign": "vcenter",
                "num_format": CURRENCY_FORMAT,
                "border": 1,
                "border_color": WHITE,
            }
        ),
        "card_score": workbook.add_format(
            {
                "bold": True,
                "font_size": 18,
                "font_color": TEAL,
                "bg_color": PALE,
                "align": "center",
                "valign": "vcenter",
                "num_format": "0.0000",
                "border": 1,
                "border_color": WHITE,
            }
        ),
        "label": workbook.add_format(
            {"bold": True, "font_color": INK, "bg_color": "#E7EEF3", "valign": "top"}
        ),
        "value": workbook.add_format(
            {"font_color": INK, "bg_color": WHITE, "valign": "top", "text_wrap": True}
        ),
        "body": workbook.add_format(
            {"font_color": INK, "valign": "top", "text_wrap": True}
        ),
        "body_currency": workbook.add_format(
            {"font_color": INK, "num_format": CURRENCY_FORMAT}
        ),
        "body_score": workbook.add_format(
            {"font_color": INK, "num_format": "0.0000"}
        ),
        "note": workbook.add_format(
            {
                "font_color": MUTED,
                "italic": True,
                "text_wrap": True,
                "valign": "top",
                "bg_color": PALE,
            }
        ),
        "metric_name": workbook.add_format(
            {
                "bold": True,
                "font_color": INK,
                "bg_color": PALE,
                "border": 1,
                "border_color": BORDER,
                "valign": "top",
            }
        ),
        "metric_description": workbook.add_format(
            {
                "font_color": INK,
                "bg_color": WHITE,
                "border": 1,
                "border_color": BORDER,
                "text_wrap": True,
                "valign": "top",
            }
        ),
    }


def create_excel_report(
    data: pd.DataFrame,
    case_name: str,
    result: RegressionResult,
    evaluation_report: pd.DataFrame,
    prediction: tuple[float, float],
    future_data: pd.DataFrame | None = None,
) -> bytes:
    """Build a styled, multi-sheet Excel report with tables and charts."""
    if case_name not in CASE_SPECS:
        raise ValueError("Selecciona el caso de terrenos o el caso de ventas.")

    spec = CASE_SPECS[case_name]
    feature = spec["feature"]
    target = spec["target"]
    ordered_data = data.sort_values(feature, kind="stable").reset_index(drop=True)
    fitted_values = result.model.predict(ordered_data[[feature]])
    model_data = pd.DataFrame(
        {
            feature: ordered_data[feature],
            target: ordered_data[target],
            "Ajuste global del modelo (S/)": fitted_values,
            "Residuo del ajuste (S/)": ordered_data[target].to_numpy() - fitted_values,
        }
    )

    if case_name == "ventas" and future_data is not None:
        projection_data = future_data.rename(
            columns={
                feature: "Mes proyectado",
                target: "Ventas proyectadas (S/)",
            }
        ).copy()
        projection_title = "Proyección de ventas"
        projection_note = (
            "Proyección lineal basada en el historial disponible. No incorpora "
            "estacionalidad ni cambios futuros en las condiciones."
        )
        projection_widths = [22, 28]
    else:
        scenario_values = [
            ("Entrada mínima", float(data[feature].min())),
            ("Entrada promedio", float(data[feature].mean())),
            ("Entrada máxima", float(data[feature].max())),
            ("Valor elegido en la aplicación", float(prediction[0])),
        ]
        scenario_features = pd.DataFrame(
            {feature: [value for _, value in scenario_values]}
        )
        scenario_predictions = result.model.predict(scenario_features)
        projection_data = pd.DataFrame(
            {
                "Escenario": [label for label, _ in scenario_values],
                feature: [value for _, value in scenario_values],
                "Precio estimado (S/)": scenario_predictions,
            }
        )
        projection_title = "Escenarios de precio"
        projection_note = (
            "Los escenarios aplican la ecuación lineal a valores representativos "
            "de área; no consideran ubicación, servicios ni características del terreno."
        )
        projection_widths = [34, 22, 28]

    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
    workbook.set_properties(
        {
            "title": f"Informe de regresión lineal - {case_name}",
            "subject": "Análisis, evaluación y proyección del modelo",
            "author": "Regresión Lab",
            "company": "Proyecto académico",
            "keywords": "regresión lineal, análisis, predicción, evaluación",
            "comments": "Generado automáticamente desde Regresión Lab.",
        }
    )
    formats = _create_formats(workbook)
    currency_format = workbook.add_format({"num_format": CURRENCY_FORMAT})
    summary = workbook.add_worksheet("Resumen")

    _, data_start_row = _table_sheet(
        workbook,
        "Datos",
        "RegressionData",
        "Historial y ajuste del modelo",
        "Residuos calculados sobre el ajuste global; para medir rendimiento imparcial, consulta Evaluación.",
        model_data,
        formats,
        [22, 25, 30, 26],
        {
            target: currency_format,
            "Ajuste global del modelo (S/)": currency_format,
            "Residuo del ajuste (S/)": currency_format,
        },
    )
    data_end_row = data_start_row + len(model_data) - 1

    evaluation_formats = {
        "Valor real (S/)": currency_format,
        "Predicción (S/)": currency_format,
        "Error (S/)": currency_format,
        "Error absoluto (S/)": currency_format,
    }
    evaluation_sheet, evaluation_start_row = _table_sheet(
        workbook,
        "Evaluación",
        "HoldoutEvaluation",
        "Evaluación con datos reservados",
        "Cada fila se reservó antes del ajuste de evaluación. Error = predicción menos valor real.",
        evaluation_report,
        formats,
        [22, 22, 22, 20, 24],
        evaluation_formats,
    )
    evaluation_end_row = evaluation_start_row + len(evaluation_report) - 1
    evaluation_sheet.conditional_format(
        evaluation_start_row,
        len(evaluation_report.columns) - 1,
        evaluation_end_row,
        len(evaluation_report.columns) - 1,
        {"type": "3_color_scale", "min_color": "#D8F3DC", "mid_color": "#FFF3BF", "max_color": "#FFC9C9"},
    )

    projection_sheet, projection_start_row = _table_sheet(
        workbook,
        "Proyección",
        "ModelProjections",
        projection_title,
        projection_note,
        projection_data,
        formats,
        projection_widths,
        {
            column: currency_format
            for column in projection_data.columns
            if column.endswith("(S/)")
        },
    )
    if case_name == "ventas" and future_data is not None:
        projection_sheet.write(
            projection_start_row + len(projection_data) + 1,
            0,
            "Total proyectado",
            formats["label"],
        )
        projection_sheet.write(
            projection_start_row + len(projection_data) + 1,
            1,
            float(future_data[target].sum()),
            formats["body_currency"],
        )

    summary.activate()
    summary.hide_gridlines(2)
    summary.set_tab_color(ORANGE)
    summary.set_landscape()
    summary.fit_to_pages(1, 1)
    summary.set_margins(0.3, 0.3, 0.45, 0.45)
    summary.set_column("A:H", 15)
    summary.set_column("I:J", 12)
    summary.set_row(0, 34)
    summary.set_row(1, 26)
    summary.merge_range(
        "A1:J2",
        "INFORME EJECUTIVO\nREGRESIÓN LINEAL",
        formats["title"],
    )
    summary.merge_range(
        "A3:J3",
        f"{case_name}  ·  Regresión Lab  ·  Reporte generado automáticamente",
        formats["subtitle"],
    )
    summary.merge_range("A5:J5", "INDICADORES CLAVE", formats["section"])

    cards = [
        ("R² DE PRUEBA", result.r2, formats["card_score"]),
        ("ERROR ABSOLUTO MEDIO · MAE", result.mae, formats["card_currency"]),
        ("RAÍZ DEL ERROR CUADRÁTICO · RMSE", result.rmse, formats["card_currency"]),
        ("PREDICCIÓN ELEGIDA", prediction[1], formats["card_currency"]),
        ("REGISTROS ANALIZADOS", len(data), formats["card_value"]),
    ]
    for column, (label, value, value_format) in zip((0, 2, 4, 6, 8), cards):
        summary.merge_range(6, column, 6, column + 1, label, formats["card_label"])
        summary.merge_range(7, column, 8, column + 1, value, value_format)
    summary.set_row(6, 27)
    summary.set_row(7, 28)
    summary.set_row(8, 24)

    summary.merge_range("A10:J10", "FICHA TÉCNICA DEL ANÁLISIS", formats["section"])
    metadata = [
        ("Caso", case_name, "Fecha", pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")),
        ("Variable de entrada", feature, "Variable objetivo", target),
        ("Registros disponibles", len(data), "Entrenamiento / prueba", f"{result.train_size} / {result.test_size}"),
        ("Rango observado", f"{data[feature].min():g} – {data[feature].max():g}", "Predicción elegida", f"{prediction[0]:g}"),
        ("Pendiente", result.slope, "Intercepto", result.intercept),
    ]
    for row, values in enumerate(metadata, start=10):
        summary.write(row, 0, values[0], formats["label"])
        summary.merge_range(row, 1, row, 3, values[1], formats["value"])
        summary.write(row, 4, values[2], formats["label"])
        summary.merge_range(row, 5, row, 9, values[3], formats["value"])
    summary.merge_range(
        "A16:J16",
        "CÓMO LEER LOS INDICADORES",
        formats["section"],
    )
    metric_notes = [
        ("R²", "Resume qué tanto explica el modelo; se calcula solo con datos reservados. Puede ser negativo."),
        ("MAE", "Error absoluto promedio de la prueba, expresado en soles. Cuanto menor, mejor."),
        ("RMSE", "Error de prueba que penaliza con más fuerza las desviaciones grandes."),
    ]
    for row, (name, description) in enumerate(metric_notes, start=16):
        summary.merge_range(row, 0, row, 1, name, formats["metric_name"])
        summary.merge_range(row, 2, row, 9, description, formats["metric_description"])
        summary.set_row(row, 30)
    summary.merge_range(
        "A20:J21",
        "IMPORTANTE · Los datos de muestra son simulados. Una proyección supone que la relación observada continúa; "
        "no incorpora factores externos y no debe interpretarse como garantía comercial.",
        formats["note"],
    )
    summary.merge_range("A23:J23", "VISUALIZACIÓN DEL AJUSTE Y LOS ERRORES", formats["section"])

    fit_chart = workbook.add_chart({"type": "scatter"})
    fit_chart.add_series(
        {
            "name": "Valores observados",
            "categories": ["Datos", data_start_row, 0, data_end_row, 0],
            "values": ["Datos", data_start_row, 1, data_end_row, 1],
            "marker": {"type": "circle", "size": 6, "border": {"color": TEAL}, "fill": {"color": TEAL}},
            "line": {"none": True},
        }
    )
    fit_chart.add_series(
        {
            "name": "Ajuste lineal",
            "categories": ["Datos", data_start_row, 0, data_end_row, 0],
            "values": ["Datos", data_start_row, 2, data_end_row, 2],
            "marker": {"type": "none"},
            "line": {"color": ORANGE, "width": 2.25},
        }
    )
    fit_chart.set_title({"name": "Historial y recta aprendida"})
    fit_chart.set_x_axis({"name": feature, "major_gridlines": {"visible": False}})
    fit_chart.set_y_axis({"name": target, "num_format": '"S/ " #,##0'})
    fit_chart.set_legend({"position": "bottom"})
    fit_chart.set_style(10)
    fit_chart.set_size({"width": 470, "height": 285})
    fit_chart.set_chartarea({"border": {"none": True}, "fill": {"color": WHITE}})
    fit_chart.set_plotarea({"border": {"color": BORDER}, "fill": {"color": PALE}})

    error_chart = workbook.add_chart({"type": "column"})
    error_chart.add_series(
        {
            "name": "Error absoluto",
            "categories": [
                "Evaluación",
                evaluation_start_row,
                0,
                evaluation_end_row,
                0,
            ],
            "values": [
                "Evaluación",
                evaluation_start_row,
                len(evaluation_report.columns) - 1,
                evaluation_end_row,
                len(evaluation_report.columns) - 1,
            ],
            "fill": {"color": TEAL},
            "border": {"none": True},
        }
    )
    error_chart.set_title({"name": "Error absoluto · datos de prueba"})
    error_chart.set_x_axis({"name": feature, "label_position": "low"})
    error_chart.set_y_axis({"name": "Error (S/)", "num_format": '"S/ " #,##0'})
    error_chart.set_legend({"none": True})
    error_chart.set_style(10)
    error_chart.set_size({"width": 470, "height": 285})
    error_chart.set_chartarea({"border": {"none": True}, "fill": {"color": WHITE}})
    error_chart.set_plotarea({"border": {"color": BORDER}, "fill": {"color": PALE}})
    summary.insert_chart("A24", fit_chart)
    summary.insert_chart("F24", error_chart)

    summary.freeze_panes(5, 0)
    summary.set_header("&LRegresión Lab&CInforme ejecutivo&R&Página &P")
    summary.set_footer("&LReporte académico&RGenerado automáticamente")
    summary.set_first_sheet()
    summary.activate()
    workbook.close()
    return buffer.getvalue()
