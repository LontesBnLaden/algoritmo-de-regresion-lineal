from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from excel_report import create_excel_report
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
        --ink: #e8eef8;
        --muted: #9aacc2;
        --teal: #45e0ce;
        --orange: #ffb86b;
        --line: #23344b;
        --panel: #101d30;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 82% 0%, rgba(35, 122, 132, .18), transparent 34%),
            #07111f;
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: rgba(7, 17, 31, .75); }
    [data-testid="stAppViewContainer"] { background: transparent; }
    .main .block-container { max-width: 1440px; padding-top: 2rem; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1a2c 0%, #101f34 58%, #0a1728 100%);
        border-right: 1px solid #20344a;
    }
    [data-testid="stSidebar"] * { color: #e8eef8; }
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] input { color: #e8eef8 !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: .3rem .45rem;
        border-radius: 8px;
    }
    .brand-mark {
        display: inline-flex; align-items: center; justify-content: center;
        width: 42px; height: 42px; margin: .2rem 0 .4rem;
        border-radius: 13px;
        background: linear-gradient(140deg, #45e0ce, #6476ff);
        color: #07111f; font-size: 1rem; font-weight: 900;
        box-shadow: 0 8px 26px rgba(69, 224, 206, .2);
    }
    .sidebar-kicker, .eyebrow {
        color: #45e0ce; font-size: .68rem; font-weight: 800;
        letter-spacing: .16em; text-transform: uppercase;
    }
    .hero {
        display: flex; align-items: center; justify-content: space-between;
        gap: 2rem; min-height: 255px;
        padding: 2.2rem 2.6rem; margin: .2rem 0 1.4rem;
        overflow: hidden; position: relative;
        border: 1px solid rgba(115, 214, 218, .2);
        border-radius: 26px; color: white;
        background:
            radial-gradient(circle at 80% 45%, rgba(69, 224, 206, .2), transparent 25%),
            linear-gradient(115deg, #101d32 0%, #102b40 54%, #124b55 100%);
        box-shadow: 0 22px 65px rgba(0, 0, 0, .28);
    }
    .hero-copy { position: relative; z-index: 1; max-width: 720px; }
    .hero h1 {
        margin: .65rem 0 .25rem; color: white;
        font-size: clamp(2.1rem, 4vw, 3.4rem); letter-spacing: -.045em;
    }
    .hero p { margin: .65rem 0 0; color: #bfd0df; font-size: 1.04rem; }
    .hero-art {
        flex: 0 0 190px; width: 190px; height: 190px;
        display: flex; align-items: center; justify-content: center;
        border: 1px solid rgba(115, 214, 218, .35); border-radius: 50%;
        background: radial-gradient(circle, rgba(69, 224, 206, .18), rgba(69, 224, 206, .015) 68%);
        box-shadow: 0 0 55px rgba(69, 224, 206, .12), inset 0 0 35px rgba(69, 224, 206, .08);
        transform: rotate(-8deg);
    }
    .hero-art-inner {
        width: 138px; height: 138px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; gap: .3rem;
        border: 1px solid rgba(115, 214, 218, .25); border-radius: 50%;
        background: rgba(7, 17, 31, .72); transform: rotate(8deg);
    }
    .hero-art-inner strong { color: #f4fbff; font-size: 1.35rem; }
    .hero-art-inner span { color: #8ca5bc; font-size: .65rem; letter-spacing: .1em; }
    .hero-pills {
        display: flex; flex-wrap: wrap; gap: .55rem;
        margin-top: 1.3rem;
    }
    .hero-pill {
        padding: .35rem .7rem;
        border: 1px solid rgba(148, 185, 206, .26);
        border-radius: 999px;
        background: rgba(255, 255, 255, .055);
        color: #d7e7f2;
        font-size: .82rem;
    }
    .section-label {
        color: var(--teal); font-weight: 800; letter-spacing: .12em;
        text-transform: uppercase; font-size: .75rem;
    }
    div[data-testid="stMetric"] {
        min-height: 106px; padding: 1rem 1.15rem;
        border: 1px solid #24364d; border-radius: 16px;
        background: linear-gradient(145deg, #122137, #0d192a);
        box-shadow: 0 12px 30px rgba(0, 0, 0, .15);
    }
    div[data-testid="stMetricLabel"] { color: #9aacc2; font-size: .82rem; }
    div[data-testid="stMetricValue"] { color: #f2f7ff; font-weight: 750; }
    div[data-testid="stAlert"] { border-radius: 12px; border: 1px solid #263a50; }
    .stButton > button, .stDownloadButton > button {
        min-height: 42px; border-radius: 11px; font-weight: 700;
    }
    .stDownloadButton > button {
        border: 1px solid rgba(69, 224, 206, .35);
        background: linear-gradient(115deg, #153a43, #173044);
        color: #b7fff4;
    }
    [data-testid="stExpander"] {
        border: 1px solid #24364d; border-radius: 15px;
        background: #0e1b2c;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid #26394f; border-radius: 13px; overflow: hidden;
    }
    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }
    [data-testid="stTabs"] [role="tablist"] {
        gap: .45rem; border-bottom: 1px solid #23344b;
    }
    [data-testid="stTabs"] button[role="tab"] {
        height: 48px; color: #91a5bd; font-weight: 750;
        border-bottom: 2px solid transparent;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #5de7d7; border-bottom-color: #45e0ce;
    }
    [data-testid="stTabContent"] { padding-top: 1.25rem; }
    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #45e0ce, #6b83ff);
    }
    h1, h2, h3 { color: #edf4ff; letter-spacing: -.02em; }
    h3 { margin-top: .5rem; }
    @media (max-width: 760px) {
        .hero { min-height: 220px; padding: 1.5rem; }
        .hero-art { display: none; }
        .main .block-container { padding: 1rem .8rem 2rem; }
        [data-testid="stTabs"] button[role="tab"] { font-size: .72rem; }
    }
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
        st.sidebar.info("Sube un CSV o elige otra fuente para continuar.")
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
    figure.patch.set_facecolor("#101d30")
    axis.set_facecolor("#101d30")
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
        edgecolor="#101d30",
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
            edgecolor="#101d30",
            linewidth=0.8,
            label="Predicción",
            zorder=5,
        )
    axis.set_xlabel(spec["feature"], color="#b4c4d8")
    axis.set_ylabel(spec["target"], color="#b4c4d8")
    axis.grid(color="#26394f", linewidth=0.8)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#40546b")
    axis.tick_params(colors="#9aacc2")
    axis.legend(
        frameon=True,
        facecolor="#101d30",
        edgecolor="#26394f",
        labelcolor="#dce8f6",
        loc="best",
    )
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
    figure.patch.set_facecolor("#101d30")
    for axis in axes:
        axis.set_facecolor("#101d30")
        axis.grid(color="#26394f", linewidth=0.8)
        axis.spines[["top", "right"]].set_visible(False)
        axis.spines[["left", "bottom"]].set_color("#40546b")
        axis.tick_params(colors="#9aacc2")

    axes[0].scatter(
        actual,
        predicted,
        color="#087f8c",
        edgecolor="#101d30",
        linewidth=0.9,
        s=75,
        zorder=3,
    )
    axes[0].plot(
        line_limits,
        line_limits,
        color="#ffb86b",
        linestyle="--",
        linewidth=2,
        label="Estimación ideal",
    )
    axes[0].set_xlim(line_limits)
    axes[0].set_ylim(line_limits)
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].set_title("Real frente a estimado", color="#e8eef8", pad=12)
    axes[0].set_xlabel("Valor real (S/)", color="#b4c4d8")
    axes[0].set_ylabel("Predicción (S/)", color="#b4c4d8")
    axes[0].legend(
        frameon=True,
        facecolor="#101d30",
        edgecolor="#26394f",
        labelcolor="#dce8f6",
        loc="best",
    )

    axes[1].axhline(0, color="#ffb86b", linestyle="--", linewidth=2)
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
        edgecolor="#101d30",
        linewidth=0.9,
        s=75,
        zorder=3,
    )
    axes[1].set_title("Error por dato reservado", color="#e8eef8", pad=12)
    axes[1].set_xlabel(spec["feature"], color="#b4c4d8")
    axes[1].set_ylabel("Error (S/)", color="#b4c4d8")

    figure.tight_layout(pad=2)
    st.pyplot(figure, width="stretch")
    plt.close(figure)


def main() -> None:
    st.sidebar.markdown('<div class="brand-mark">RL</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-kicker">DATA / LAB</div>', unsafe_allow_html=True)
    st.sidebar.markdown("## Regresión Lab")
    st.sidebar.caption("Un espacio para explorar relaciones y hacer predicciones.")
    st.sidebar.markdown("---")
    case_label = st.sidebar.radio("Selecciona un caso", list(CASES))
    case = CASES[case_label]
    case_key = case["key"]

    st.sidebar.markdown("### Configura el análisis")
    source = st.sidebar.radio(
        "Fuente del historial",
        ["Datos de ejemplo", "Editar tabla", "Importar CSV"],
        help="Los archivos de ejemplo incluyen más de 20 registros.",
    )
    sample_data = read_sample(case_key)
    st.sidebar.download_button(
        "Descargar CSV de ejemplo",
        data=sample_data.to_csv(index=False).encode("utf-8"),
        file_name=case["file"],
        mime="text/csv",
        width="stretch",
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("MODELO ACTIVO")
    st.sidebar.markdown("**Regresión lineal simple**")
    st.sidebar.caption("Una variable · evaluación separada · predicción reproducible")

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-copy">
                <div class="eyebrow">REGRESSION WORKSPACE · 01</div>
                <h1>{case['icon']} {case_label}</h1>
                <p>{case['description']} Explora los datos, evalúa el ajuste y prueba escenarios.</p>
                <div class="hero-pills">
                    <span class="hero-pill">● Datos validados</span>
                    <span class="hero-pill">↗ Modelo entrenado</span>
                    <span class="hero-pill">◈ Resultados interpretables</span>
                </div>
            </div>
            <div class="hero-art" aria-hidden="true">
                <div class="hero-art-inner">
                    <span>MODELO LINEAL</span>
                    <strong>y = mx + b</strong>
                    <span>DATOS → DECISIÓN</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview_tab, prediction_tab, diagnostics_tab, data_tab = st.tabs(
        ["01  RESUMEN", "02  PREDICCIÓN", "03  DIAGNÓSTICO", "04  DATOS"]
    )

    try:
        with data_tab:
            st.markdown("### 🗂️ Centro de datos")
            st.caption(
                "Consulta el historial del análisis o modifica la tabla desde la fuente "
                "configurada en el panel lateral."
            )
            data = load_selected_data(case_key, source)
            result = train_and_evaluate(data, case_key)
            st.dataframe(data, hide_index=True, width="stretch")
            st.download_button(
                "Descargar historial utilizado",
                data=data.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"historial_{case_key}.csv",
                mime="text/csv",
            )
    except ValueError as error:
        st.error(str(error))
        st.stop()

    spec = CASE_SPECS[case_key]
    evaluation_report = build_evaluation_report(result, case_key)
    report_csv = evaluation_report.to_csv(index=False).encode("utf-8-sig")
    future_data = None
    if case_key == "ventas":
        future_months = np.arange(
            int(data[spec["feature"]].max()) + 1,
            int(data[spec["feature"]].max()) + 7,
        )
        future_data = pd.DataFrame({spec["feature"]: future_months})
        future_data[spec["target"]] = result.model.predict(future_data)

    formula_sign = "+" if result.intercept >= 0 else "−"
    equation = (
        rf"\hat{{y}} = {result.slope:.2f}\,x "
        rf"{formula_sign} {abs(result.intercept):.2f}"
    )
    prediction_value: float
    prediction_amount: float
    with prediction_tab:
        st.markdown('<div class="section-label">INTERACTIVE FORECAST</div>', unsafe_allow_html=True)
        st.markdown("### Construye un escenario")
        st.caption(
            "Cambia el valor de entrada y observa cómo responde la recta aprendida."
        )
        chart_column, prediction_column = st.columns([1.55, 1], gap="large")
        with prediction_column:
            with st.container(border=True):
                st.markdown("#### Tu predicción")
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
                    "Resultado estimado",
                    f"S/ {prediction_amount:,.2f}",
                    delta=(
                        f"{prediction_value:g} "
                        + ("m²" if case_key == "terrenos" else "mes")
                    ),
                )
                st.latex(equation)
                st.caption(
                    "Estimación basada en una sola variable; no contempla otros "
                    "factores que pueden influir en el resultado."
                )
        with chart_column:
            st.markdown("#### Recta, historial y escenario")
            render_history_chart(
                data,
                case_key,
                result,
                (prediction_value, prediction_amount),
                future_data,
            )
        if case_key == "ventas" and future_data is not None:
            st.markdown("#### Proyección de los próximos 6 meses")
            forecast_columns = st.columns(2)
            forecast_columns[0].metric(
                "Total proyectado",
                f"S/ {future_data[spec['target']].sum():,.2f}",
            )
            forecast_columns[1].metric(
                "Promedio mensual proyectado",
                f"S/ {future_data[spec['target']].mean():,.2f}",
            )
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

    with overview_tab:
        st.markdown('<div class="section-label">MODEL OVERVIEW</div>', unsafe_allow_html=True)
        if len(data) < 20:
            st.warning(
                f"Hay {len(data)} registros. La actividad pide al menos 20 por caso; "
                "agrega más filas o importa un CSV más completo."
            )
        else:
            st.success(f"Historial listo: {len(data)} registros numéricos validados.")
        st.markdown("### Resumen del modelo")
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

        st.markdown("#### Rendimiento con datos reservados")
        metric_columns = st.columns(5)
        metric_columns[0].metric("R² de prueba", f"{result.r2:.4f}")
        metric_columns[1].metric("MAE de prueba", f"S/ {result.mae:,.2f}")
        metric_columns[2].metric("RMSE de prueba", f"S/ {result.rmse:,.2f}")
        metric_columns[3].metric("Entrenamiento", f"{result.train_size}")
        metric_columns[4].metric("Prueba", f"{result.test_size}")
        score_progress = float(np.clip(result.r2, 0.0, 1.0))
        st.progress(score_progress, text=f"R² en escala visual de 0 a 1: {result.r2:.4f}")
        st.caption(
            "Los meses finales se reservan para probar ventas; en terrenos se usa "
            "una selección aleatoria reproducible. Un R² negativo significa que el "
            "modelo rindió peor que predecir el promedio."
        )
        excel_report = create_excel_report(
            data=data,
            case_name=case_key,
            result=result,
            evaluation_report=evaluation_report,
            prediction=(prediction_value, prediction_amount),
            future_data=future_data,
        )
        st.download_button(
            "Exportar informe Excel profesional",
            data=excel_report,
            file_name=f"informe_regresion_{case_key}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help=(
                "Libro con resumen ejecutivo, métricas explicadas, datos, "
                "evaluación reservada, proyecciones y gráficos."
            ),
        )

        equation_column, explanation_column = st.columns([1, 1.25], gap="large")
        with equation_column:
            with st.container(border=True):
                st.markdown("#### Ecuación aprendida")
                st.latex(equation)
        with explanation_column:
            with st.container(border=True):
                st.markdown("#### ¿Qué significa?")
                direction = "aumenta" if result.slope >= 0 else "disminuye"
                st.write(
                    f"Por cada unidad adicional de **{spec['feature']}**, el modelo "
                    f"estima que **{spec['target']} {direction} S/ "
                    f"{abs(result.slope):,.2f}**."
                )
                st.caption(
                    "Los CSV incluidos son simulados para practicar. El modelo "
                    "representa una relación lineal simple, no una garantía."
                )

    with diagnostics_tab:
        st.markdown('<div class="section-label">MODEL CHECK</div>', unsafe_allow_html=True)
        st.markdown("### ¿Qué tan cerca predice?")
        st.caption(
            "En el panel izquierdo, los puntos cercanos a la diagonal se ajustan mejor. "
            "En el derecho, errores próximos a cero son menores. Se muestran solo "
            "registros reservados durante la evaluación."
        )
        render_evaluation_charts(evaluation_report, case_key)
        st.download_button(
            "Descargar evaluación detallada (CSV)",
            data=report_csv,
            file_name=f"evaluacion_{case_key}.csv",
            mime="text/csv",
            help="Incluye valores reales, predicciones y errores por registro reservado.",
        )
        with st.expander("Ver errores de cada dato de prueba"):
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
        with st.expander("Interpretación y límites del modelo"):
            st.write(
                f"El error absoluto medio (MAE) es **S/ {result.mae:,.2f}**. "
                f"El RMSE es **S/ {result.rmse:,.2f}** y penaliza más los errores grandes."
            )
            st.markdown(
                """
                - Los datos de muestra son simulados, no cotizaciones ni ventas reales.
                - La regresión usa una sola variable y supone una relación aproximadamente lineal.
                - Las proyecciones fuera del rango histórico pueden ser poco confiables.
                - Para decisiones reales, recopila datos representativos y considera otros factores.
                """
            )

    st.caption(
        "REGRESIÓN LAB  ·  Python · pandas · scikit-learn · Matplotlib"
    )


if __name__ == "__main__":
    main()
