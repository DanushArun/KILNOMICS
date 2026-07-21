"""FastAPI entrypoint for the local KILNOMICS pilot."""

import tempfile
from dataclasses import asdict
from pathlib import Path
from threading import Thread
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.analysis import analyze_workbook, evaluate_scenario
from backend.app.data_quality import inspect_workbook
from backend.app.demo import create_demo_workbook
from backend.app.runs import RunStore
from backend.app.summary import workbook_summary
from backend.app.training import train_workbook


_ANALYSES: dict[str, dict[str, object]] = {}
_RUNS = RunStore()


def create_app() -> FastAPI:
    """Create the local-only API application."""
    app = FastAPI(title="KILNOMICS", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.get("/api/health")(_health)
    app.get("/api/demo-workbook")(_demo_workbook)
    app.post("/api/workbooks/train")(_train_workbook)
    app.post("/api/workbooks/train/start")(_start_training)
    app.get("/api/workbooks/runs/{run_id}")(_training_status)
    app.post("/api/scenarios")(_evaluate_scenario)
    return app


def _health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-private-pilot"}


def _demo_workbook() -> FileResponse:
    output = Path(tempfile.gettempdir()) / "KILNOMICS_Demo_Data.xlsx"
    create_demo_workbook(output)
    return FileResponse(output, filename=output.name)


async def _train_workbook(workbook: UploadFile = File(...)) -> dict[str, object]:
    if not workbook.filename or not workbook.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Upload an .xlsx workbook")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / workbook.filename
        path.write_bytes(await workbook.read())
        try:
            return _analysis_response(path, workbook.filename)
        except (KeyError, ValueError) as error:
            raise HTTPException(status_code=422, detail=str(error)) from error


async def _start_training(workbook: UploadFile = File(...)) -> dict[str, str]:
    if not workbook.filename or not workbook.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Upload an .xlsx workbook")
    run_id = _RUNS.create()
    contents = await workbook.read()
    worker = Thread(target=_run_training, args=(run_id, workbook.filename, contents), daemon=True)
    worker.start()
    return {"run_id": run_id}


def _training_status(run_id: str) -> dict[str, object]:
    try:
        return {"run_id": run_id, **_RUNS.snapshot(run_id)}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


def _run_training(run_id: str, filename: str, contents: bytes) -> None:
    try:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / filename
            path.write_bytes(contents)
            _RUNS.update(run_id, "validating", 5)
            data_status = inspect_workbook(path)
            _RUNS.update(run_id, "training", 30)
            reports = train_workbook(path)
            _RUNS.update(run_id, "analysing", 75)
            result = _analysis_response(path, filename, reports, data_status)
        _RUNS.complete(run_id, result)
    except (KeyError, ValueError) as error:
        _RUNS.fail(run_id, str(error))


def _analysis_response(
    path: Path,
    filename: str,
    reports: dict[str, object] | None = None,
    data_status: object | None = None,
) -> dict[str, object]:
    reports = train_workbook(path) if reports is None else reports
    data_status = inspect_workbook(path) if data_status is None else data_status
    summary = workbook_summary(path)
    analysis = analyze_workbook(path)
    analysis_id = str(uuid4())
    _ANALYSES[analysis_id] = analysis
    return {
        "source": filename,
        "summary": summary,
        "data_status": asdict(data_status),
        "reports": {name: asdict(report) for name, report in reports.items()},
        "analysis_id": analysis_id,
        **analysis,
    }


def _evaluate_scenario(payload: dict[str, object]) -> dict[str, object]:
    analysis_id = str(payload.get("analysis_id", ""))
    analysis = _ANALYSES.get(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis expired. Upload the workbook again.")
    plant_id = str(payload.get("plant_id", ""))
    inputs = payload.get("inputs", {})
    if not isinstance(inputs, dict):
        raise HTTPException(status_code=422, detail="Scenario inputs must be an object.")
    try:
        return evaluate_scenario(analysis, plant_id, inputs)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


app = create_app()
