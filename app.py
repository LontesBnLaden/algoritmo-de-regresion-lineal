from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from regression import (
    CASE_SPECS,
    build_evaluation_report,
    prepare_dataset,
    train_and_evaluate,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

st.set_page_config(
    page_title="Regresión Lab | Predicción",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #142b4a;
        --muted: #64748b;
        --teal: #087f8c;
        --orange: #e88943;
        --line: #e4ebf3;
    }
    .stApp { background: #f4f7fb; color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(244, 247, 251, .92); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #102743 0%, #173c59 100%);
    }
    [data-testid="stSidebar"] * { color: #f2f7fb; }
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] input { color: #142b4a !important; }
    .hero {
        padding: 1.7rem 2rem;
        margin: .2rem 0 1.3rem;
        border-radius: 20px;
        color: white;
        background: linear-gradient(120deg, #102743 0%, #087f8c 100%);
        box-shadow: 0 12px 30px rgba(16, 39, 67, .13);
    }
    .hero h1 { margin: 0; color: white; font-size: 2rem; }
    .hero p { margin: .45rem 0 0; color: #e1f4f4; font-size: 1rem; }
    .hero-pills {
        display: flex; flex-wrap: wrap; gap: .55rem;
        margin-top: 1rem;
    }
    .hero-pill {
        padding: .35rem .7rem;
        border: 1px solid rgba(225, 244, 244, .35);
        border-radius: 999px;
        background: rgba(255, 255, 255, .1);
        color: #f2fbfb;
        font-size: .82rem;
    }
    .section-label {
        color: #087f8c; font-weight: 700; letter-spacing: .08em;
        text-transform: uppercase; font-size: .75rem;
    }
    div[data-testid="stMetric"] {
        padding: 1rem 1.1rem;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: white;
        box-shadow: 0 4px 14px rgba(20, 43, 74, .04);
    }
    div[data-testid="stMetricLabel"] { color: var(--muted); }
    div[data-testid="stMetricValue"] { color: var(--ink); }
    div[data-testid="stAlert"] { border-radius: 12px; }
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
    }
    .stDownloadButton > button {
        border: 1px solid #cfe2e8;
        background: #edf8f8;
        color: #075e68;
        font-weight: 650;
    }
    [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: white;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }
    h2, h3 { color: var(--ink); }
    </style>
    """,
    unsafe_allow_html=True,
)

CASES = {
    "Precio de terrenos": {
        "key": "terrenos",
        "file": "terrenos.csv",
        "description": "Estima el precio de un terreno a partir de su área.",
        "icon": "🏡",
    },
    "Ventas mensuales": {
        "key": "ventas",
        "file": "ventas.csv",
        "description": "Proyecta las ventas de un empleado según el mes.",
        "icon": "📊",
    },
}


def read_sample(case_key: str) -> pd.DataFrame:
    filename = next(item["file"] for item in CASES.values() if item["key"] == case_key)
    return pd.read_csv(DATA_DIR / filename)


def load_selected_data(case_key: str, source: str) -> pd.DataFrame:
    if source == "Datos de ejemplo":
        return prepare_dataset(read_sample(case_key), case_key)

    if source == "Editar tabla":
        sample = prepare_dataset(read_sample(case_key), case_key)
        with st.expander("✍️ Ver y editar el historial", expanded=True):
            st.caption(
                "Edita las celdas o agrega filas al final. Los cambios se usan "
                "inmediatamente al ejecutar el modelo."
            )
            edited = st.data_editor(
                sample,
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                key=f"editor-{case_key}",
                column_config={
                    CASE_SPECS[case_key]["feature"]: st.column_config.NumberColumn(
                        CASE_SPECS[case_key]["feature"], min_value=0
                    ),
                    CASE_SPECS[case_key]["target"]: st.column_config.NumberColumn(
                        CASE_SPECS[case_key]["target"], min_value=0, format="S/ %.2f"
                    ),
                },
            )
        return prepare_dataset(edited, case_key)

    uploaded_file = st.sidebar.file_uploader(
        "Elige un archivo CSV",
        type=["csv"],
        help="El archivo debe tener una columna de entrada y otra de resultado.",
        key=f"upload-{case_key}",
    )
    if uploaded_file is None:
        st.info("Sube un archivo CSV o cambia la fuente a «Datos de ejemplo».")
        st.stop()
    try:
        uploaded = pd.read_csv(BytesIO(uploaded_file.getvalue()), encoding="utf-8-sig")
    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"No se pudo leer el CSV: {error}")
        st.stop()
    return prepare_dataset(uploaded, case_key)


def render_history_chart(
    data: pd.DataFrame,
    case_key: str,
    result,
    prediction: tuple[float, float] | None = None,
    future_data: pd.DataFrame | None = None,
) -> None:
    spec = CASE_SPECS[case_key]
    maximum_x = data[spec["feature"]].max()
    if future_data is not None:
        maximum_x = future_data[spec["feature"]].max()
    x_values = np.linspace(data[spec["feature"]].min(), maximum_x, 200)
    y_values = result.model.predict(pd.DataFrame({spec["feature"]: x_values}))

    figure, axis = plt.subplots(figsize=(8, 4.3), dpi=120)
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    axis.scatter(
        data[spec["feature"]],
        data[spec["target"]],
        color="#087f8c",
        s=48,
        alpha=0.85,
        label="Datos históricos",
        zorder=3,
    )
    axis.scatter(
        result.test_features[spec["feature"]],
        result.test_actual,
        color="#e88943",
        s=68,
        marker="D",
        edgecolor="white",
        linewidth=0.9,
        label="Datos reservados para prueba",
        zorder=4,
    )
    axis.plot(x_values, y_values, color="#e88943", linewidth=2.7, label="Recta ajustada")
    if future_data is not None:
        axis.plot(
            future_data[spec["feature"]],
            future_data[spec["target"]],
            color="#7063bd",
            marker="s",
            linestyle="--",
            linewidth=2,
            label="Proyección 6 meses",
            zorder=4,
        )
    if prediction is not None:
        axis.scatter(
            [prediction[0]],
            [prediction[1]],
            color="#d34e5c",
            marker="*",
            s=190,
            edgecolor="white",
            linewidth=0.8,
            label="Predicción",
            zorder=5,
        )
    axis.set_xlabel(spec["feature"], color="#40536a")
    axis.set_ylabel(spec["target"], color="#40536a")
    axis.grid(color="#e7edf4", linewidth=0.8)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#d5dee8")
    axis.tick_params(colors="#64748b")
    axis.legend(frameon=False, loc="best")
    figure.tight_layout()
    st.pyplot(figure, width="stretch")
    plt.close(figure)


def render_evaluation_charts(
    evaluation_report: pd.DataFrame, case_key: str
) -> None:
    spec = CASE_SPECS[case_key]
    actual = evaluation_report["Valor real (S/)"]
    predicted = evaluation_report["Predicción (S/)"]
    residuals = evaluation_report["Error (S/)"]
    lower = min(float(actual.min()), float(predicted.min()))
    upper = max(float(actual.max()), float(predicted.max()))
    padding = max((upper - lower) * 0.06, 1.0)
    line_limits = (lower - padding, upper + padding)

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2), dpi=120)
    figure.patch.set_facecolor("white")
    for axis in axes:
        axis.set_facecolor("white")
        axis.grid(color="#e7edf4", linewidth=0.8)
        axis.spines[["top", "right"]].set_visible(False)
        axis.spines[["left", "bottom"]].set_color("#d5dee8")
        axis.tick_params(colors="#64748b")

    axes[0].scatter(
        actual,
        predicted,
        color="#087f8c",
        edgecolor="white",
        linewidth=0.9,
        s=75,
        zorder=3,
    )
    axes[0].plot(
        line_limits,
        line_limits,
        color="#e88943",
        linestyle="--",
        linewidth=2,
        label="Estimación ideal",
    )
    axes[0].set_xlim(line_limits)
    axes[0].set_ylim(line_limits)
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].set_title("Real frente a estimado", color="#142b4a", pad=12)
    axes[0].set_xlabel("Valor real (S/)")
    axes[0].set_ylabel("Predicción (S/)")
    axes[0].legend(frameon=False, loc="best")

    axes[1].axhline(0, color="#e88943", linestyle="--", linewidth=2)
    axes[1].vlines(
        evaluation_report[spec["feature"]],
        0,
        residuals,
        color="#a6d9d7",
        linewidth=2,
        alpha=0.85,
    )
    axes[1].scatter(
        evaluation_report[spec["feature"]],
        residuals,
        color="#087f8c",
        edgecolor="white",
        linewidth=0.9,
        s=75,
        zorder=3,
    )
    axes[1].set_title("Error por dato reservado", color="#142b4a", pad=12)
    axes[1].set_xlabel(spec["feature"])
    axes[1].set_ylabel("Error (S/)")

    figure.tight_layout(pad=2)
    st.pyplot(figure, width="stretch")
    plt.close(figure)


def main() -> None:
    st.sidebar.markdown("## 📈 Regresión Lab")
    st.sidebar.caption("Aprende, evalúa y predice con tus datos")
    st.sidebar.markdown("---")
    case_label = st.sidebar.radio("Selecciona un caso", list(CASES))
    case = CASES[case_label]
    case_key = case["key"]

    st.sidebar.markdown("### Fuente de datos")
    source = st.sidebar.radio(
        "¿Cómo quieres cargar el historial?",
        ["Datos de ejemplo", "Editar tabla", "Importar CSV"],
        help="Los archivos de ejemplo incluyen más de 20 registros.",
    )
    sample_data = read_sample(case_key)
    st.sidebar.download_button(
        "⬇️ Descargar CSV de ejemplo",
        data=sample_data.to_csv(index=False).encode("utf-8"),
        file_name=case["file"],
        mime="text/csv",
        width="stretch",
    )

    st.markdown(
        f"""
        <div class="hero">
            <div class="section-label" style="color:#b9eff0">PRÁCTICA CALIFICADA · REGRESIÓN LINEAL</div>
            <h1>{case['icon']} {case_label}</h1>
            <p>{case['description']} Revisa los datos, mide el error y explora predicciones.</p>
            <div class="hero-pills">
                <span class="hero-pill">🧾 Datos editables</span>
                <span class="hero-pill">📐 Modelo lineal</span>
                <span class="hero-pill">🔍 Evaluación visual</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        data = load_selected_data(case_key, source)
        result = train_and_evaluate(data, case_key)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    spec = CASE_SPECS[case_key]
    if len(data) < 20:
        st.warning(
            f"Hay {len(data)} registros. La actividad pide al menos 20 por caso; "
            "agrega más filas o importa un CSV más completo."
        )
    else:
        st.success(f"Historial listo: {len(data)} registros numéricos validados.")

    st.markdown("### 🧭 Resumen del conjunto")
    profile_columns = st.columns(3)
    profile_columns[0].metric("Registros analizados", f"{len(data)}")
    profile_columns[1].metric(
        "Rango de entrada",
        (
            f"{data[spec['feature']].min():g} – "
            f"{data[spec['feature']].max():g} "
            f"{'m²' if case_key == 'terrenos' else 'meses'}"
        ),
    )
    average_label = "Precio promedio" if case_key == "terrenos" else "Venta promedio"
    profile_columns[2].metric(
        average_label,
        f"S/ {data[spec['target']].mean():,.2f}",
    )

    st.markdown(
        '<div class="section-label">Evaluación con datos no vistos</div>',
        unsafe_allow_html=True,
    )
    metric_columns = st.columns(5)
    metric_columns[0].metric("R² de prueba", f"{result.r2:.4f}")
    metric_columns[1].metric("MAE de prueba", f"S/ {result.mae:,.2f}")
    metric_columns[2].metric("RMSE de prueba", f"S/ {result.rmse:,.2f}")
    metric_columns[3].metric("Para entrenar", f"{result.train_size} registros")
    metric_columns[4].metric("Para evaluar", f"{result.test_size} registros")
    st.caption(
        "En ventas, la prueba usa los meses más recientes para respetar el orden "
        "temporal. En terrenos se reserva una muestra aleatoria reproducible. "
        "Un R² negativo indica que el modelo rindió peor que predecir el promedio."
    )
    evaluation_report = build_evaluation_report(result, case_key)
    report_csv = evaluation_report.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Descargar evaluación detallada (CSV)",
        data=report_csv,
        file_name=f"evaluacion_{case_key}.csv",
        mime="text/csv",
        help="Incluye valores reales, predicciones y errores de cada registro de prueba.",
    )

    formula_sign = "+" if result.intercept >= 0 else "−"
    st.markdown("### La ecuación aprendida")
    st.latex(
        rf"\hat{{y}} = {result.slope:.2f}\,x {formula_sign} {abs(result.intercept):.2f}"
    )
    future_data = None
    if case_key == "ventas":
        future_months = np.arange(
            int(data[spec["feature"]].max()) + 1,
            int(data[spec["feature"]].max()) + 7,
        )
        future_data = pd.DataFrame({spec["feature"]: future_months})
        future_data[spec["target"]] = result.model.predict(future_data)

    chart_column, prediction_column = st.columns([1.35, 1])
    with chart_column:
        st.markdown("### Datos y recta de regresión")
        prediction_value: float
        prediction_amount: float
        with prediction_column:
            st.markdown("### Prueba una predicción")
            if case_key == "terrenos":
                prediction_value = st.number_input(
                    "Área del terreno (m²)",
                    min_value=0.0,
                    value=220.0,
                    step=10.0,
                    format="%.2f",
                )
            else:
                prediction_value = float(
                    st.number_input(
                        "Número del mes que quieres estimar",
                        min_value=1,
                        value=int(data[spec["feature"]].max()) + 1,
                        step=1,
                    )
                )
            prediction_amount = float(
                result.model.predict(
                    pd.DataFrame({spec["feature"]: [prediction_value]})
                )[0]
            )
            st.metric(
                "Estimación del modelo",
                f"S/ {prediction_amount:,.2f}",
                delta=f"{prediction_value:g} " + ("m²" if case_key == "terrenos" else "mes"),
            )
            if case_key == "terrenos":
                st.caption(
                    "Estimación basada solo en el área; no considera ubicación, "
                    "servicios ni características del terreno."
                )
            else:
                st.caption(
                    "La tendencia supone que las condiciones observadas continúan "
                    "sin cambios."
                )
        render_history_chart(
            data,
            case_key,
            result,
            (prediction_value, prediction_amount),
            future_data,
        )

    if case_key == "ventas" and future_data is not None:
        st.markdown("### Proyección de los próximos 6 meses")
        st.dataframe(
            future_data.rename(
                columns={
                    spec["feature"]: "Mes futuro",
                    spec["target"]: "Ventas estimadas (S/)",
                }
            ).style.format({"Ventas estimadas (S/)": "S/ {:,.2f}"}),
            hide_index=True,
            width="stretch",
        )
        st.caption(
            f"Total proyectado para los seis meses: "
            f"S/ {future_data[spec['target']].sum():,.2f}."
        )

    st.markdown("### 🔎 Diagnóstico visual del modelo")
    st.caption(
        "En el gráfico de la izquierda, los puntos más cercanos a la diagonal "
        "tienen predicciones más precisas. A la derecha, los errores cercanos a "
        "cero son menores. Solo se muestran datos reservados para la evaluación."
    )
    render_evaluation_charts(evaluation_report, case_key)

    with st.expander("📘 Interpretación y límites del modelo"):
        direction = "aumenta" if result.slope >= 0 else "disminuye"
        st.write(
            f"Por cada unidad adicional de **{spec['feature']}**, el modelo estima "
            f"que **{spec['target']} {direction} S/ {abs(result.slope):,.2f}**, "
            f"según estos datos."
        )
        st.write(
            f"El R² de prueba es **{result.r2:.4f}** y el error absoluto medio "
            f"(MAE) es **S/ {result.mae:,.2f}**. El MAE describe el error promedio "
            f"en las unidades de dinero del ejemplo. El RMSE es **S/ {result.rmse:,.2f}** "
            "y penaliza más los errores grandes."
        )
        st.markdown(
            """
            - Los CSV incluidos son datos simulados para practicar; no son cotizaciones ni ventas reales.
            - La regresión usa una sola variable y supone una relación aproximadamente lineal.
            - Una proyección fuera del rango histórico puede ser poco confiable.
            - Para decisiones reales, recopila datos representativos y considera más factores.
            """
        )

    with st.expander("🧾 Ver historial utilizado"):
        st.dataframe(data, hide_index=True, width="stretch")

    with st.expander("🧪 Ver predicciones de prueba y errores"):
        st.caption(
            "Estos registros se reservaron antes de entrenar; el error se calcula "
            "como predicción menos valor real."
        )
        st.dataframe(
            evaluation_report.style.format(
                {
                    "Valor real (S/)": "S/ {:,.2f}",
                    "Predicción (S/)": "S/ {:,.2f}",
                    "Error (S/)": "S/ {:,.2f}",
                    "Error absoluto (S/)": "S/ {:,.2f}",
                }
            ),
            hide_index=True,
            width="stretch",
        )

    st.markdown("---")
    st.caption(
        "Trabajo académico · Regresión lineal simple · Python, pandas, "
        "scikit-learn y Matplotlib"
    )


if __name__ == "__main__":
    main()
