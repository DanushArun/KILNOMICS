# KILNOMICS pilot

Local Excel-to-insight prototype for clinker and cement cost optimisation.

## Run

```bash
./.venv/bin/uvicorn backend.app.main:app --port 8000
cd frontend && npm run dev
```

Open `http://localhost:5173`, download or upload `demo/KILNOMICS_Demo_Data.xlsx`,
then wait for the temporal model-training report.

## Data contract

The demo workbook contains the screenshot-template sheets: `README`, plant, material,
fuel, constituent, kiln, target, recipe, and daily process sheets. It also includes
`CostAssumptions` and `RawMixDaily`, which are required to calculate traceable costs.

All demo values are synthetic. The dashboard hides a learned target when it fails the
configured temporal validation gate.
