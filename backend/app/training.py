"""Time-aware soft-sensor model training from imported workbooks."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from backend.app.model_gate import ModelMetrics, passes_release_gate


@dataclass(frozen=True)
class TargetReport:
    """Evaluation output and fitted model for one predictive target."""

    target: str
    metrics: ModelMetrics
    passed: bool
    model_name: str
    interval_radius: float
    input_features: tuple[str, ...]
    sample_count: int
    holdout_count: int


TARGETS = {
    "C3S": ("ClinkerDaily", "C3S", 2.0),
    "fCaO": ("ClinkerDaily", "fCaO_mean", 0.2),
    "SHC": ("EnergyDaily", "SHC_kcalkg", 10.0),
    "Strength28d": ("CementDaily", "str_28d_MPa", 1.0),
}


def train_workbook(path: Path) -> dict[str, TargetReport]:
    """Fit model candidates and return release-gated reports for every target."""
    sheets = pd.read_excel(path, sheet_name=None)
    source = _joined_features(sheets)
    return {name: _train_target(source, name, config) for name, config in TARGETS.items()}


def _joined_features(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    kiln = sheets["KilnFeedDaily"].copy()
    process = sheets["ProcessDaily"].copy()
    fuel = sheets["FuelDaily"].copy()
    clinker = sheets["ClinkerDaily"].copy()
    energy = sheets["EnergyDaily"].copy()
    cement = sheets["CementDaily"].copy()
    keys = ["plant_id", "date", "shift"]
    merged = kiln.merge(process, on=keys, suffixes=("", "_process"))
    merged = merged.merge(fuel[keys + ["TSR_pct"]], on=keys)
    merged = merged.merge(clinker[keys + ["C3S", "fCaO_mean"]], on=keys)
    energy_daily = energy.groupby(["plant_id", "date"], as_index=False).first()
    merged = merged.merge(energy_daily[["plant_id", "date", "SHC_kcalkg"]], on=["plant_id", "date"])
    return _merge_daily_cement(merged, cement)


def _merge_daily_cement(source: pd.DataFrame, cement: pd.DataFrame) -> pd.DataFrame:
    daily = cement.groupby(["plant_id", "date"], as_index=False).first()
    columns = ["plant_id", "date", "clinker_factor", "blaine_m2kg", "str_28d_MPa"]
    return source.merge(daily[columns], on=["plant_id", "date"])


def _train_target(source: pd.DataFrame, name: str, config: tuple[str, str, float]) -> TargetReport:
    _, target_column, max_mae = config
    model_source = _daily_average(source) if target_column in {"SHC_kcalkg", "str_28d_MPa"} else source
    features = _features_for(target_column)
    plant_reports = [_train_plant(frame, target_column, max_mae, features) for _, frame in model_source.groupby("plant_id")]
    metrics = _aggregate_metrics([item[0] for item in plant_reports])
    model_name = _plurality([item[1] for item in plant_reports])
    interval_radius = float(np.mean([item[2] for item in plant_reports]))
    return TargetReport(
        name, metrics, passes_release_gate(metrics, max_mae), model_name, interval_radius,
        tuple(features), sum(item[3] for item in plant_reports), sum(item[4] for item in plant_reports),
    )


def _daily_average(source: pd.DataFrame) -> pd.DataFrame:
    """Average shift-level predictors before fitting daily laboratory targets."""
    return source.groupby(["plant_id", "date"], as_index=False).mean(numeric_only=True)


def _train_plant(
    frame: pd.DataFrame, target: str, max_mae: float, features: list[str]
) -> tuple[ModelMetrics, str, float, int, int]:
    data = frame.sort_values(["date", "shift"]).dropna(subset=features + [target])
    x_values = data[features].astype(float).to_numpy()
    y_values = data[target].astype(float).to_numpy()
    metrics, model_name, radius, holdout_count = _evaluate_candidates(x_values, y_values, max_mae)
    return metrics, model_name, radius, len(data), holdout_count


def _features_for(target: str) -> list[str]:
    shared = ["LSF", "SM", "AM", "false_air_pct", "TSR_pct"]
    if target == "str_28d_MPa":
        return ["C3S", "fCaO_mean", "clinker_factor", "blaine_m2kg"]
    if target == "SHC_kcalkg":
        return shared + ["PH_exit_temp_C", "secondary_air_temp_C"]
    return shared + ["burning_zone_temp_C"]


def _evaluate_candidates(
    x_values: np.ndarray, y_values: np.ndarray, max_mae: float
) -> tuple[ModelMetrics, str, float, int]:
    candidates = {
        "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "HistGradientBoosting": HistGradientBoostingRegressor(max_iter=120, max_leaf_nodes=8, l2_regularization=1.0, random_state=42),
    }
    results = {name: _evaluate_model(model, x_values, y_values, max_mae) for name, model in candidates.items()}
    name = min(results, key=lambda candidate: results[candidate][0].mae)
    metrics, radius, holdout_count = results[name]
    return metrics, name, radius, holdout_count


def _evaluate_model(
    model: object, x_values: np.ndarray, y_values: np.ndarray, max_mae: float
) -> tuple[ModelMetrics, float, int]:
    splits = TimeSeriesSplit(n_splits=4, gap=1)
    predictions, actuals, baselines, fold_mae = [], [], [], []
    for train_index, test_index in splits.split(x_values):
        model.fit(x_values[train_index], y_values[train_index])
        predicted = model.predict(x_values[test_index])
        observed = y_values[test_index]
        predictions.extend(predicted)
        actuals.extend(observed)
        baselines.extend([y_values[train_index][-1]] * len(test_index))
        fold_mae.append(mean_absolute_error(observed, predicted))
    metrics, radius = _metrics(actuals, predictions, baselines, fold_mae, max_mae)
    return metrics, radius, len(actuals)


def _metrics(actuals: list[float], predictions: list[float], baselines: list[float], fold_mae: list[float], max_mae: float) -> tuple[ModelMetrics, float]:
    residuals = np.abs(np.subtract(actuals, predictions))
    mae = float(mean_absolute_error(actuals, predictions))
    baseline_mae = float(mean_absolute_error(actuals, baselines))
    radius = float(np.quantile(residuals, 0.9))
    coverage = float(np.mean(residuals <= radius))
    metrics = ModelMetrics(
        float(r2_score(actuals, predictions)), mae,
        100 * (baseline_mae - mae) / max(baseline_mae, 0.001), coverage,
        max(fold_mae) / max(max_mae, 0.001),
    )
    return metrics, radius


def _aggregate_metrics(metrics: list[ModelMetrics]) -> ModelMetrics:
    values = np.array([[metric.r_squared, metric.mae, metric.baseline_improvement_pct, metric.interval_coverage, metric.worst_fold_ratio] for metric in metrics])
    return ModelMetrics(*np.mean(values, axis=0).tolist())


def _plurality(values: list[str]) -> str:
    return max(set(values), key=values.count)
