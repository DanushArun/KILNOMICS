"""Validation gates for learned soft-sensor models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelMetrics:
    """Temporal validation metrics for a single target model."""

    r_squared: float
    mae: float
    baseline_improvement_pct: float
    interval_coverage: float
    worst_fold_ratio: float


def passes_release_gate(metrics: ModelMetrics, max_mae: float) -> bool:
    """Return whether all agreed model-release thresholds are satisfied."""
    return (
        metrics.r_squared >= 0.8
        and metrics.mae <= max_mae
        and metrics.baseline_improvement_pct >= 15
        and 0.85 <= metrics.interval_coverage <= 0.95
        and metrics.worst_fold_ratio <= 1.0
    )
