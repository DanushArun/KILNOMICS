"""Workbook-derived portfolio analysis for the client-facing dashboard."""

from pathlib import Path

import pandas as pd


def analyze_workbook(path: Path) -> dict[str, object]:
    """Return a traceable portfolio view for one uploaded workbook."""
    sheets = pd.read_excel(path, sheet_name=None)
    plants = [_plant_result(sheets, plant) for plant in sheets["PlantMaster"].to_dict("records")]
    opportunities = _opportunities(plants)
    total = round(sum(item["annual_savings_rs"] for item in opportunities), 2)
    return {
        "provenance": _provenance(sheets),
        "portfolio": _portfolio(total, opportunities),
        "plants": plants,
        "benchmarks": _benchmarks(plants),
        "opportunities": opportunities,
        "finance_status": {"state": "not_started", "realised_annual_rs": 0},
    }


def _provenance(sheets: dict[str, pd.DataFrame]) -> dict[str, str]:
    readme = sheets.get("README", pd.DataFrame()).astype(str).to_string().lower()
    mode = "simulated" if "synthetic" in readme or "simulated" in readme else "uploaded_unverified"
    return {
        "mode": mode,
        "label": "Simulated portfolio" if mode == "simulated" else "Uploaded workbook",
        "disclaimer": "Illustrative opportunity only; no finance-realised savings.",
    }


def _plant_result(sheets: dict[str, pd.DataFrame], plant: dict[str, object]) -> dict[str, object]:
    plant_id = str(plant["plant_id"])
    recipe = _for_plant(sheets["ProductRecipe"], plant_id).iloc[0]
    energy = _for_plant(sheets["EnergyDaily"], plant_id)
    process = _for_plant(sheets["ProcessDaily"], plant_id)
    fuel = _for_plant(sheets["FuelDaily"], plant_id)
    costs = _for_plant(sheets["CostAssumptions"], plant_id).iloc[0]
    clinker_cost = _clinker_cost(sheets, plant_id, energy, costs)
    cement_cost = _cement_cost(sheets, plant_id, recipe, energy, costs, clinker_cost)
    fuel_cost = _activity_cost(
        sheets["FuelDaily"], sheets["FuelLibrary"], plant_id, "fuel_id", "qty_tonnes",
        float(energy["clinker_tonnes"].sum()),
    )
    constituents = _for_plant(sheets["CementConstituents"], plant_id).set_index("id")
    return {
        "plant_id": plant_id,
        "plant_name": plant["plant_name"],
        "rated_clinker_tpd": float(plant["rated_clinker_tpd"]),
        "structure": _structure_label(plant),
        "clinker_cost_per_t": round(clinker_cost, 2),
        "cement_cost_per_t": round(cement_cost, 2),
        "contribution_per_t": round(float(recipe["NSR_per_ton"]) - cement_cost, 2),
        "monthly_volume_t": float(recipe["monthly_volume_t"]),
        "shc_kcalkg": round(float(energy["SHC_kcalkg"].mean()), 2),
        "tsr_pct": round(float(fuel["TSR_pct"].mean()), 2),
        "clinker_factor_pct": round(float(recipe["clinker_factor"]) * 100, 2),
        "false_air_pct": round(float(process["false_air_pct"].mean()), 2),
        "limits": _limits(sheets, plant_id),
        "fuel_cost_per_t": fuel_cost,
        "scm_cost_per_t": float(constituents.loc[recipe["scm_id"], "costPerTon"]),
        "fossil_cost_per_kcal": _heat_cost(sheets, plant_id, False),
        "alternative_cost_per_kcal": _heat_cost(sheets, plant_id, True),
        "gypsum_pct": float(recipe["gypsum_pct"]) * 100,
    }


def _for_plant(frame: pd.DataFrame, plant_id: str) -> pd.DataFrame:
    return frame.loc[frame["plant_id"] == plant_id]


def _structure_label(plant: dict[str, object]) -> str:
    return (
        f"{plant['preheater_stages']}-stage PH · {plant['cement_mill_type']} "
        f"· WHR {plant['WHR_capacity_MW']} MW"
    )


def _limits(sheets: dict[str, pd.DataFrame], plant_id: str) -> dict[str, float]:
    kiln = _for_plant(sheets["KilnConfig"], plant_id).iloc[0]
    recipe = _for_plant(sheets["ProductRecipe"], plant_id).iloc[0]
    scm = _for_plant(sheets["CementConstituents"], plant_id)
    row = scm.loc[scm["id"] == recipe["scm_id"]].iloc[0]
    return {
        "tsr_max_pct": float(kiln["tsrMaxPct"]),
        "scm_min_pct": float(row["BIS_min_pct"]),
        "scm_max_pct": float(row["BIS_max_pct"]),
    }


def _clinker_cost(
    sheets: dict[str, pd.DataFrame],
    plant_id: str,
    energy: pd.DataFrame,
    costs: pd.Series,
) -> float:
    clinker = float(energy["clinker_tonnes"].sum())
    fuel = _activity_cost(
        sheets["FuelDaily"], sheets["FuelLibrary"], plant_id, "fuel_id", "qty_tonnes", clinker
    )
    raw = _activity_cost(
        sheets["RawMixDaily"], sheets["MaterialSources"], plant_id, "material_id", "tonnes", clinker
    )
    power_columns = ["kWh_crushing", "kWh_rawgrind", "kWh_kilnfans", "kWh_coalmill"]
    power = float(energy[power_columns].sum(axis=1).mean())
    power *= float(costs["grid_power_rs_per_kwh"])
    fixed = float(costs["stores_rs_per_clinker_t"])
    fixed += float(costs["additives_rs_per_clinker_t"])
    return fuel + raw + power + fixed


def _activity_cost(
    activity: pd.DataFrame,
    library: pd.DataFrame,
    plant_id: str,
    key: str,
    quantity: str,
    clinker: float,
) -> float:
    source = _for_plant(activity, plant_id)
    prices = _for_plant(library, plant_id)[["id", "costPerTon"]]
    matched = source.merge(prices, left_on=key, right_on="id", how="inner")
    return float((matched[quantity] * matched["costPerTon"]).sum() / clinker)


def _cement_cost(
    sheets: dict[str, pd.DataFrame], plant_id: str, recipe: pd.Series, energy: pd.DataFrame,
    costs: pd.Series, clinker_cost: float,
) -> float:
    constituents = _for_plant(sheets["CementConstituents"], plant_id).set_index("id")
    scm_cost = float(constituents.loc[recipe["scm_id"], "costPerTon"])
    gypsum_cost = float(constituents.loc["gypsum", "costPerTon"])
    grinding = float(energy["kWh_cementgrind"].mean()) * float(costs["grid_power_rs_per_kwh"])
    freight = float(recipe["lead_distance_km"]) * float(costs["freight_rs_per_tkm"])
    return (
        clinker_cost * float(recipe["clinker_factor"])
        + scm_cost * float(recipe["scm_pct"])
        + gypsum_cost * float(recipe["gypsum_pct"])
        + grinding + freight
    )


def _heat_cost(sheets: dict[str, pd.DataFrame], plant_id: str, alternative: bool) -> float:
    fuels = _for_plant(sheets["FuelLibrary"], plant_id)
    biogenic = fuels["biogenicFraction"].fillna(0).astype(float) > 0
    candidates = fuels.loc[biogenic if alternative else ~biogenic]
    if candidates.empty:
        return 0.0
    costs = candidates["costPerTon"].astype(float)
    heat = candidates["ncvKcalPerKg"].astype(float) * 1_000
    return float((costs / heat).min())


def _opportunities(plants: list[dict[str, object]]) -> list[dict[str, object]]:
    targets = {
        "shc": min(float(plant["shc_kcalkg"]) for plant in plants),
        "tsr": max(float(plant["tsr_pct"]) for plant in plants),
        "clinker_factor": min(float(plant["clinker_factor_pct"]) for plant in plants),
    }
    actions: list[dict[str, object]] = []
    for plant in plants:
        actions.extend(_plant_opportunities(plant, targets))
    return actions


def _plant_opportunities(
    plant: dict[str, object], targets: dict[str, float]
) -> list[dict[str, object]]:
    volume = float(plant["monthly_volume_t"]) * 12
    shc = float(plant["shc_kcalkg"])
    tsr = float(plant["tsr_pct"])
    clinker = float(plant["clinker_factor_pct"])
    tsr_target = min(targets["tsr"], float(plant["limits"]["tsr_max_pct"]))
    clinker_floor = 100 - float(plant["limits"]["scm_max_pct"]) - float(plant["gypsum_pct"])
    clinker_target = max(targets["clinker_factor"], clinker_floor)
    heat_delta = max(float(plant["fossil_cost_per_kcal"]) - float(plant["alternative_cost_per_kcal"]), 0)
    actions = [
        _action(
            plant, "Heat efficiency", "SHC", shc, targets["shc"],
            float(plant["fuel_cost_per_t"]) / max(shc, 1), volume,
        ),
        _action(
            plant, "Alternative fuels", "TSR", tsr, tsr_target,
            shc * 10 * heat_delta, volume,
        ),
        _action(
            plant, "Clinker factor", "Clinker factor", clinker, clinker_target,
            (float(plant["clinker_cost_per_t"]) - float(plant["scm_cost_per_t"])) / 100,
            volume,
        ),
    ]
    return [action for action in actions if action["annual_savings_rs"] > 0]


def _action(
    plant: dict[str, object],
    lever: str,
    metric: str,
    baseline: float,
    target: float,
    value_per_point: float,
    volume: float,
) -> dict[str, object]:
    delta = abs(float(baseline) - float(target))
    savings_per_t = round(delta * value_per_point, 2)
    return {
        "id": f"{plant['plant_id']}-{lever.lower().replace(' ', '-')}",
        "plant_id": plant["plant_id"],
        "plant_name": plant["plant_name"],
        "lever": lever,
        "metric": metric,
        "baseline": round(float(baseline), 2),
        "target": round(float(target), 2),
        "savings_per_t": savings_per_t,
        "annual_savings_rs": round(savings_per_t * volume, 2),
        "confidence": "illustrative",
        "state": "investigate",
    }


def _portfolio(total: float, opportunities: list[dict[str, object]]) -> dict[str, object]:
    return {
        "annual_savings_rs": total,
        "practical_annual_savings_rs": 0,
        "opportunity_count": len(opportunities),
    }


def _benchmarks(plants: list[dict[str, object]]) -> list[dict[str, object]]:
    best_shc = min(float(plant["shc_kcalkg"]) for plant in plants)
    return [
        {
            "plant_id": plant["plant_id"],
            "metric": "SHC",
            "value": plant["shc_kcalkg"],
            "gap_to_best": round(float(plant["shc_kcalkg"]) - best_shc, 2),
        }
        for plant in plants
    ]


def evaluate_scenario(
    analysis: dict[str, object], plant_id: str, inputs: dict[str, float]
) -> dict[str, object]:
    """Return a bounded scenario for a plant already present in an analysis."""
    plant = _find_plant(analysis["plants"], plant_id)
    target_tsr = float(inputs.get("tsr_pct", plant["tsr_pct"]))
    constraints = _scenario_constraints(plant, target_tsr)
    if any(item["state"] == "blocked" for item in constraints):
        return {
            "feasible": False,
            "annual_savings_rs": 0,
            "savings_per_t": 0,
            "constraints": constraints,
        }
    annual = float(plant["monthly_volume_t"]) * 12
    delta = max(target_tsr - float(plant["tsr_pct"]), 0)
    heat_cost_delta = max(
        float(plant["fossil_cost_per_kcal"]) - float(plant["alternative_cost_per_kcal"]), 0
    )
    savings_per_t = delta / 100 * float(plant["shc_kcalkg"]) * 1_000 * heat_cost_delta
    return {
        "feasible": True,
        "annual_savings_rs": round(savings_per_t * annual, 2),
        "savings_per_t": round(savings_per_t, 2),
        "constraints": constraints,
    }


def _find_plant(plants: object, plant_id: str) -> dict[str, object]:
    for plant in plants:
        if plant["plant_id"] == plant_id:
            return plant
    raise ValueError(f"Unknown plant: {plant_id}")


def _scenario_constraints(plant: dict[str, object], target_tsr: float) -> list[dict[str, str]]:
    maximum = float(plant["limits"]["tsr_max_pct"])
    if target_tsr > maximum:
        return [{
            "name": "Thermal substitution",
            "state": "blocked",
            "message": f"TSR exceeds the {maximum:g}% plant capability limit.",
        }]
    return [{
        "name": "Thermal substitution",
        "state": "pass",
        "message": "Target is within the plant capability limit.",
    }]
