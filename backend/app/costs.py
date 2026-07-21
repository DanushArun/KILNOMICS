"""Cost and savings calculations."""


def annualized_savings(before_per_ton: float, after_per_ton: float, monthly_volume: float) -> float:
    """Return annual savings from a per-tonne reduction and monthly volume."""
    if monthly_volume < 0:
        raise ValueError("monthly volume cannot be negative")
    return (before_per_ton - after_per_ton) * monthly_volume * 12
