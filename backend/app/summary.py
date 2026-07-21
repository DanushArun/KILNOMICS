"""Workbook-derived cost summaries for dashboard and scenario baselines."""

from pathlib import Path

import pandas as pd


def workbook_summary(path: Path) -> dict[str, float]:
    """Calculate current cost and contribution metrics from workbook inputs."""
    sheets = pd.read_excel(path, sheet_name=None)
    recipe = sheets["ProductRecipe"].iloc[0]
    costs = sheets["CostAssumptions"].iloc[0]
    clinker_cost = _clinker_cost(sheets, costs)
    cement_cost = _cement_cost(sheets, recipe, costs, clinker_cost)
    return {
        "clinker_cost_per_t": round(clinker_cost, 2),
        "cement_cost_per_t": round(cement_cost, 2),
        "contribution_per_t": round(float(recipe["NSR_per_ton"]) - cement_cost, 2),
        "clinker_factor_pct": float(recipe["clinker_factor"]) * 100,
        "scm_pct": float(recipe["scm_pct"]) * 100,
        "monthly_volume_t": float(recipe["monthly_volume_t"]),
        "shc_kcalkg": round(float(sheets["EnergyDaily"]["SHC_kcalkg"].mean()), 2),
    }


def _clinker_cost(sheets: dict[str, pd.DataFrame], costs: pd.Series) -> float:
    energy = sheets["EnergyDaily"]
    fuel = sheets["FuelDaily"]
    fuels = sheets["FuelLibrary"]
    materials = sheets["MaterialSources"]
    raw_mix = sheets["RawMixDaily"]
    fuel_cost = _matched_cost(fuel, fuels, "fuel_id") / energy["clinker_tonnes"].mean()
    raw_cost = _matched_cost(raw_mix, materials, "material_id") / energy["clinker_tonnes"].mean()
    power = energy[["kWh_crushing", "kWh_rawgrind", "kWh_kilnfans", "kWh_coalmill"]].sum(axis=1).mean()
    power_cost = power * float(costs["grid_power_rs_per_kwh"])
    return fuel_cost + raw_cost + power_cost + float(costs["stores_rs_per_clinker_t"]) + float(costs["additives_rs_per_clinker_t"])


def _matched_cost(activity: pd.DataFrame, library: pd.DataFrame, key: str) -> float:
    library_key = "id"
    merged = activity.merge(library[[library_key, "costPerTon"]], left_on=key, right_on=library_key)
    quantity = "qty_tonnes" if "qty_tonnes" in merged else "tonnes"
    return float((merged[quantity] * merged["costPerTon"]).mean())


def _cement_cost(sheets: dict[str, pd.DataFrame], recipe: pd.Series, costs: pd.Series, clinker_cost: float) -> float:
    constituents = sheets["CementConstituents"]
    scm_cost = float(constituents.loc[constituents["id"] == recipe["scm_id"], "costPerTon"].iloc[0])
    gypsum_cost = float(constituents.loc[constituents["id"] == "gypsum", "costPerTon"].iloc[0])
    energy = sheets["EnergyDaily"]
    grinding = energy["kWh_cementgrind"].mean() * float(costs["grid_power_rs_per_kwh"])
    freight = float(recipe["lead_distance_km"]) * float(costs["freight_rs_per_tkm"])
    return clinker_cost * float(recipe["clinker_factor"]) + scm_cost * float(recipe["scm_pct"]) + gypsum_cost * float(recipe["gypsum_pct"]) + grinding + freight
