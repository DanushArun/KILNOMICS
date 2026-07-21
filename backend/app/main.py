"""FastAPI entrypoint for the local KILNOMICS pilot."""

import tempfile
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.demo import create_demo_workbook
from backend.app.summary import workbook_summary
from backend.app.training import train_workbook


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
            reports = train_workbook(path)
            summary = workbook_summary(path)
        except (KeyError, ValueError) as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
    return {"source": workbook.filename, "summary": summary, "reports": {name: asdict(report) for name, report in reports.items()}}


app = create_app()
