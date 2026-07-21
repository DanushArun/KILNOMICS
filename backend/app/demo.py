"""Synthetic, explicitly non-client, workbook generation."""

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


PLANTS = (
    ("DEMO_SIROHI", "Demo Sirohi", 11_500, 0.0),
    ("DEMO_DURG", "Demo Durg", 8_000, 8.0),
    ("DEMO_UDAIPUR", "Demo Udaipur", 6_500, 15.0),
)


def create_demo_workbook(path: Path, days: int = 180) -> Path:
    """Write a reproducible workbook with realistic, but synthetic, process data."""
    rng = np.random.default_rng(42)
    sheets = _static_sheets()
    sheets.update(_time_series_sheets(days, rng))
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name, index=False)
    return path


def _static_sheets() -> dict[str, pd.DataFrame]:
    plants = [plant[0] for plant in PLANTS]
    return {
        "README": pd.DataFrame({"KILNOMICS demo workbook": ["Synthetic data only. Replace with plant history before using recommendations."]}),
        "PlantMaster": pd.DataFrame(_plant_rows()),
        "MaterialSources": pd.DataFrame(_material_rows(plants)),
        "FuelLibrary": pd.DataFrame(_fuel_rows(plants)),
        "CementConstituents": pd.DataFrame(_constituent_rows(plants)),
        "KilnConfig": pd.DataFrame(_kiln_rows()),
        "Targets": pd.DataFrame(_target_rows(plants)),
        "ProductRecipe": pd.DataFrame(_recipe_rows()),
        "CostAssumptions": pd.DataFrame(_cost_rows(plants)),
    }


def _plant_rows() -> list[dict[str, object]]:
    return [
        {
            "plant_id": plant_id,
            "plant_name": name,
            "kiln_line_id": "K1",
            "rated_clinker_tpd": capacity,
            "preheater_stages": 5,
            "calciner_type": "in-line",
            "cooler_generation": "modern",
            "raw_mill_type": "VRM",
            "coal_mill_type": "vertical",
            "cement_mill_type": "VRM",
            "WHR_capacity_MW": 12,
            "altitude_m": 400,
            "kiln_residence_lag_days": 1,
            "cement_silo_lag_days": 2,
        }
        for plant_id, name, capacity, _ in PLANTS
    ]


def _material_rows(plants: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    materials = (
        ("limestone", "Main limestone", 50.5, 4.2, 1.1, 0.6, 420),
        ("laterite", "Laterite corrective", 1.0, 25.0, 20.0, 35.0, 1_600),
        ("sand", "Silica corrective", 1.0, 88.0, 4.0, 1.0, 1_200),
    )
    for plant_id in plants:
        for item_id, name, cao, sio2, al2o3, fe2o3, cost in materials:
            rows.append({
                "plant_id": plant_id, "id": item_id, "name": name,
                "category": "limestone" if item_id == "limestone" else "corrective",
                "CaO": cao, "SiO2": sio2, "Al2O3": al2o3, "Fe2O3": fe2o3,
                "MgO": 1.8, "K2O": 0.5, "Na2O": 0.1, "SO3": 0.1, "Cl": 0.01,
                "LOI": 40.2, "moisturePct": 3.0, "hardnessGrindability": 12,
                "coarseQuartzPct": 2.5, "coarseCalcitePct": 6.0, "costPerTon": cost,
                "availabilityTpm": 600_000, "minUsagePct": 0, "maxUsagePct": 100,
            })
    return rows


def _fuel_rows(plants: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    fuels = (("petcoke", 8_200, 0.8, 5.5, 0.02, 14_500), ("rdf", 3_500, 15, 0.4, 0.6, 1_500))
    for plant_id in plants:
        for fuel_id, ncv, ash, sulfur, chlorine, cost in fuels:
            rows.append({
                "plant_id": plant_id, "id": fuel_id, "name": fuel_id.upper(),
                "category": fuel_id, "ncvKcalPerKg": ncv, "moisturePct": 1.5,
                "ashPct": ash, "volatileMatterPct": 11, "sulfurPct": sulfur,
                "chlorinePct": chlorine, "HGI": 45, "biogenicFraction": 0.6 if fuel_id == "rdf" else 0,
                "ash_CaO": 2, "ash_SiO2": 40, "ash_Al2O3": 25, "ash_Fe2O3": 12,
                "ash_MgO": 1, "ash_K2O": 1, "ash_Na2O": 0.5, "ash_SO3": 3,
                "allowedInMainBurner": fuel_id == "petcoke", "maxHeatSharePct": 100 if fuel_id == "petcoke" else 25,
                "costPerTon": cost, "availabilityTpm": 30_000,
            })
    return rows


def _constituent_rows(plants: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for plant_id in plants:
        rows.extend([
            {"plant_id": plant_id, "id": "flyash", "name": "Thermal PP fly ash", "type": "flyash", "costPerTon": 1_500, "availabilityTpm": 50_000, "BIS_min_pct": 15, "BIS_max_pct": 35, "strength_activity_index": 82, "moisture_pct": 1, "blaine_m2kg": 420},
            {"plant_id": plant_id, "id": "gypsum", "name": "Gypsum", "type": "gypsum", "costPerTon": 2_500, "availabilityTpm": 20_000, "BIS_min_pct": 3, "BIS_max_pct": 5, "strength_activity_index": 0, "moisture_pct": 2, "blaine_m2kg": 0},
        ])
    return rows


def _kiln_rows() -> list[dict[str, object]]:
    return [{"plant_id": plant_id, "clinkerTPD": capacity, "dustLoss": 0.02, "freeLime": 1.2, "bypassAvailable": False, "tsrMaxPct": 16, "mainBurnerMinPct": 40} for plant_id, _, capacity, _ in PLANTS]


def _target_rows(plants: list[str]) -> list[dict[str, object]]:
    targets = (("LSF", 96, 98, True), ("SM", 2.3, 2.6, True), ("AM", 1.3, 1.6, True), ("C3S", 58, 64, False), ("MgO", 0, 5, True), ("Cl", 0, 0.015, True), ("ML_R2", 0.8, None, True))
    return [{"plant_id": plant_id, "parameter": key, "min": low, "max": high, "hard": hard, "comment": "Demo target"} for plant_id in plants for key, low, high, hard in targets]


def _recipe_rows() -> list[dict[str, object]]:
    return [{"plant_id": plant_id, "product": "PPC", "BIS_type": "PPC", "target_grade_MPa": 33, "clinker_factor": 0.68, "scm_id": "flyash", "scm_pct": 0.29, "gypsum_pct": 0.03, "target_blaine_m2kg": 330, "NSR_per_ton": 4_880 - offset * 10, "monthly_volume_t": 150_000, "lead_distance_km": 470} for plant_id, _, _, offset in PLANTS]


def _cost_rows(plants: list[str]) -> list[dict[str, object]]:
    return [{"plant_id": plant_id, "grid_power_rs_per_kwh": 7.2, "freight_rs_per_tkm": 0.8, "stores_rs_per_clinker_t": 45, "additives_rs_per_clinker_t": 30, "currency": "INR"} for plant_id in plants]


def _time_series_sheets(days: int, rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    rows = [_process_row(plant, day, shift, rng) for plant in PLANTS for day in range(days) for shift in range(1, 4)]
    return _split_time_series(rows)


def _process_row(plant: tuple[str, str, int, float], day: int, shift: int, rng: np.random.Generator) -> dict[str, object]:
    plant_id, _, capacity, offset = plant
    current_date = date(2026, 1, 1) + timedelta(days=day)
    false_air = 4.5 + rng.normal(0, 0.8)
    lsf = 96.8 + rng.normal(0, 0.45)
    tsr = np.clip(10 + rng.normal(0, 2), 4, 16)
    c3s = 61 + 2.2 * (lsf - 96.8) - 0.4 * tsr + rng.normal(0, 0.12)
    fca0 = max(0.35, 1.15 + 0.55 * (lsf - 96.8) + rng.normal(0, 0.11))
    shc = 695 + offset + 5 * false_air - tsr + rng.normal(0, 1.5)
    return {"plant_id": plant_id, "date": current_date.isoformat(), "shift": shift, "feed_rate_tph": capacity / 24 / 3, "LSF": lsf, "SM": 2.45 + rng.normal(0, 0.05), "AM": 1.42 + rng.normal(0, 0.04), "CaO": 43, "SiO2": 13.6, "Al2O3": 3.3, "Fe2O3": 2.3, "MgO": 1.7, "TSR_pct": tsr, "C3S": c3s, "C2S": 14, "C3A": 7.6, "C4AF": 10.9, "fCaO_mean": fca0, "fCaO_SD": 0.35, "litre_weight_gL": 1290, "clinker_tonnes": capacity / 3, "cement_tonnes": capacity / 3 * 1.12, "SHC_kcalkg": shc, "false_air_pct": false_air, "burning_zone_temp_C": 1450, "PH_exit_temp_C": 310, "PH_exit_O2_pct": 3.2, "PH_exit_CO_pct": 0.02, "secondary_air_temp_C": 980, "kiln_torque_pct": 72, "downtime_min": 0, "downtime_cause": "", "clinker_factor": 0.68, "blaine_m2kg": 330, "str_28d_MPa": 50 + (c3s - 60) + rng.normal(0, 0.15)}


def _split_time_series(rows: list[dict[str, object]]) -> dict[str, pd.DataFrame]:
    frame = pd.DataFrame(rows)
    shared = ["plant_id", "date", "shift"]
    daily = frame.groupby(["plant_id", "date"], as_index=False).mean(numeric_only=True)
    return {
        "KilnFeedDaily": frame[shared + ["feed_rate_tph", "LSF", "SM", "AM", "CaO", "SiO2", "Al2O3", "Fe2O3", "MgO"]],
        "FuelDaily": _fuel_daily(frame),
        "ClinkerDaily": frame[shared + ["C3S", "C2S", "C3A", "C4AF", "fCaO_mean", "fCaO_SD", "litre_weight_gL", "LSF", "SM", "AM", "MgO"]],
        "CementDaily": daily[["plant_id", "date", "clinker_factor", "blaine_m2kg", "str_28d_MPa"]].assign(product="PPC", residue_45um_pct=6, str_1d_MPa=16, str_3d_MPa=29, str_7d_MPa=38, setting_init_min=140, setting_final_min=205, soundness_mm=1),
        "EnergyDaily": daily[["plant_id", "date", "clinker_tonnes", "cement_tonnes", "SHC_kcalkg"]].assign(kWh_crushing=3, kWh_rawgrind=15, kWh_kilnfans=22, kWh_coalmill=4, kWh_cementgrind=34, kWh_utilities=8, WHR_generation_kWh=240_000),
        "ProcessDaily": frame[shared + ["burning_zone_temp_C", "PH_exit_temp_C", "PH_exit_O2_pct", "PH_exit_CO_pct", "secondary_air_temp_C", "false_air_pct", "kiln_torque_pct", "downtime_min", "downtime_cause"]],
        "CircLoad": frame[["plant_id", "date"]].assign(hotmeal_SO3_pct=4.2, hotmeal_Cl_pct=0.45, hotmeal_alkali_Na2Oeq_pct=1.1, bypass_dust_tonnes=12, alkali_sulfur_ratio=1.05),
        "RawMixDaily": _raw_mix_daily(frame),
    }


def _fuel_daily(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame[["plant_id", "date", "shift", "TSR_pct"]].copy()
    result["fuel_id"] = "petcoke"
    result["qty_tonnes"] = 210
    result["as_fired_NCV_kcalkg"] = 8180
    return result


def _raw_mix_daily(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame[["plant_id", "date", "shift"]].copy()
    result["material_id"] = "limestone"
    result["usage_pct"] = 82.0
    result["tonnes"] = frame["clinker_tonnes"] * 1.55
    return result
