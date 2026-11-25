"""Data validation and regression helpers shared by the interface and tests."""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


CASE_SPECS = {
    "terrenos": {
        "feature": "Area (m²)",
        "target": "Precio (S/)",
        "feature_aliases": {
            "area",
            "area_m2",
            "superficie",
            "metros_cuadrados",
            "m2",
        },
        "target_aliases": {
            "precio",
            "precio_s",
            "costo",
            "costo_s",
            "coste",
        },
    },
    "ventas": {
        "feature": "Mes",
        "target": "Ventas (S/)",
        "feature_aliases": {"mes", "mes_numero", "numero_mes", "month", "periodo"},
        "target_aliases": {"ventas", "ventas_s", "venta", "sales"},
    },
}


@dataclass
class RegressionResult:
    model: LinearRegression
    slope: float
    intercept: float
    r2: float
    mae: float
    train_size: int
    test_size: int
    test_features: pd.DataFrame
    test_actual: pd.Series
    test_predictions: np.ndarray


def _normalize_column_name(column: object) -> str:
    normalized = unicodedata.normalize("NFKD", str(column))
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def prepare_dataset(data: pd.DataFrame, case_name: str) -> pd.DataFrame:
    """Return a validated two-column numeric dataset with canonical labels."""
    if case_name not in CASE_SPECS:
        raise ValueError("Selecciona el caso de terrenos o el caso de ventas.")
    if data.empty:
        raise ValueError("El archivo o la tabla no contiene registros.")

    spec = CASE_SPECS[case_name]
    normalized_columns = {
        _normalize_column_name(column): column for column in data.columns
    }
    feature_key = next(
        (key for key in normalized_columns if key in spec["feature_aliases"]), None
    )
    target_key = next(
        (key for key in normalized_columns if key in spec["target_aliases"]), None
    )
    if feature_key is None or target_key is None:
        raise ValueError(
            f"Se requieren las columnas '{spec['feature']}' y '{spec['target']}'. "
            "Usa los encabezados del archivo de ejemplo o sus nombres equivalentes."
        )

    frame = pd.DataFrame(
        {
            spec["feature"]: pd.to_numeric(
                data[normalized_columns[feature_key]], errors="coerce"
            ),
            spec["target"]: pd.to_numeric(
                data[normalized_columns[target_key]], errors="coerce"
            ),
        }
    )
    if frame.isna().any().any():
        raise ValueError(
            "Hay celdas vacías o valores no numéricos. Corrige los datos antes "
            "de entrenar el modelo."
        )
    if not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError("Los datos deben contener únicamente números finitos.")
    if frame[spec["feature"]].le(0).any():
        raise ValueError(f"Los valores de '{spec['feature']}' deben ser mayores que cero.")
    if frame[spec["target"]].lt(0).any():
        raise ValueError(f"Los valores de '{spec['target']}' no pueden ser negativos.")
    if case_name == "ventas":
        months = frame[spec["feature"]].to_numpy(dtype=float)
        if not np.equal(months, np.floor(months)).all():
            raise ValueError("Los valores de 'Mes' deben ser números enteros.")
        frame = frame.sort_values(spec["feature"], kind="stable")
    if len(frame) < 5:
        raise ValueError(
            "Se necesitan al menos 5 registros para separar entrenamiento y "
            "prueba y calcular R² de forma confiable."
        )
    return frame.reset_index(drop=True)


def train_and_evaluate(data: pd.DataFrame, case_name: str) -> RegressionResult:
    """Evaluate on a held-out set, then fit a prediction model on all records."""
    frame = prepare_dataset(data, case_name)
    spec = CASE_SPECS[case_name]
    features = frame[[spec["feature"]]]
    target = frame[spec["target"]]

    test_size = max(2, math.ceil(len(frame) * 0.2))
    indices = np.arange(len(frame))
    if case_name == "ventas":
        split_at = len(frame) - test_size
        train_indices, test_indices = indices[:split_at], indices[split_at:]
    else:
        train_indices, test_indices = train_test_split(
            indices, test_size=test_size, random_state=42
        )

    evaluation_model = LinearRegression()
    evaluation_model.fit(features.iloc[train_indices], target.iloc[train_indices])
    test_features = features.iloc[test_indices]
    test_actual = target.iloc[test_indices]
    test_predictions = evaluation_model.predict(test_features)

    prediction_model = LinearRegression()
    prediction_model.fit(features, target)

    return RegressionResult(
        model=prediction_model,
        slope=float(prediction_model.coef_[0]),
        intercept=float(prediction_model.intercept_),
        r2=float(r2_score(test_actual, test_predictions)),
        mae=float(mean_absolute_error(test_actual, test_predictions)),
        train_size=len(train_indices),
        test_size=len(test_indices),
        test_features=test_features,
        test_actual=test_actual,
        test_predictions=test_predictions,
    )
