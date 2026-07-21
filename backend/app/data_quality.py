"""Workbook readiness evidence for KILNOMICS training runs."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_SHEETS = (
    "PlantMaster", "MaterialSources", "FuelLibrary", "CementConstituents",
    "KilnConfig", "Targets", "ProductRecipe", "KilnFeedDaily", "FuelDaily",
    "ClinkerDaily", "CementDaily", "EnergyDaily", "ProcessDaily", "CircLoad",
    "CostAssumptions", "RawMixDaily",
)

DAILY_SHEETS = (
    "KilnFeedDaily", "FuelDaily", "ClinkerDaily", "CementDaily", "EnergyDaily",
    "ProcessDaily", "CircLoad", "RawMixDaily",
)


@dataclass(frozen=True)
class SheetStatus:
    """Readiness record for one expected workbook sheet."""

    name: str
    row_count: int
    status: str


@dataclass(frozen=True)
class WorkbookStatus:
    """Visible data-quality evidence attached to a training run."""

    overall_status: str
    start_date: str | None
    end_date: str | None
    sheets: tuple[SheetStatus, ...]


def inspect_workbook(path: Path) -> WorkbookStatus:
    """Return sheet completeness and available daily-data span."""
    sheets = pd.read_excel(path, sheet_name=None)
    statuses = tuple(_sheet_statuses(sheets))
    start_date, end_date = _date_coverage(sheets)
    is_ready = all(item.status == "ready" for item in statuses)
    return WorkbookStatus("ready" if is_ready else "blocked", start_date, end_date, statuses)


def _sheet_statuses(sheets: dict[str, pd.DataFrame]) -> list[SheetStatus]:
    return [
        SheetStatus(name, len(sheets.get(name, pd.DataFrame())), _sheet_state(name, sheets))
        for name in REQUIRED_SHEETS
    ]


def _sheet_state(name: str, sheets: dict[str, pd.DataFrame]) -> str:
    sheet = sheets.get(name)
    if sheet is None:
        return "missing"
    return "ready" if not sheet.empty else "empty"


def _date_coverage(sheets: dict[str, pd.DataFrame]) -> tuple[str | None, str | None]:
    values = [_sheet_dates(sheets.get(name, pd.DataFrame())) for name in DAILY_SHEETS]
    dates = pd.concat(values).dropna()
    if dates.empty:
        return None, None
    return dates.min().date().isoformat(), dates.max().date().isoformat()


def _sheet_dates(sheet: pd.DataFrame) -> pd.Series:
    if "date" not in sheet:
        return pd.Series(dtype="datetime64[ns]")
    return pd.to_datetime(sheet["date"], errors="coerce")
