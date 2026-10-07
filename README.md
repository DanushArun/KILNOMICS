![KILNOMICS workflow](docs/assets/project-overview.svg)

# KILNOMICS

**Trace the value case from workbook to evidence to constrained scenario.**

A local clinker-to-cement analysis dashboard that turns an Excel workbook into cost,
quality, energy and model-evidence views. It separates potential value from validated
and finance-realised savings.


![FastAPI](https://img.shields.io/badge/FastAPI-181f28)
![React](https://img.shields.io/badge/React-181f28)
![scikit-learn](https://img.shields.io/badge/scikit--learn-181f28)

[Architecture](docs/ARCHITECTURE.md) · [Evaluation guide](docs/EVALUATION.md)

**Contents:** [The challenge](#the-challenge) · [Walkthrough](#walk-through-the-project) ·
[Implementation](#implementation-state) · [Design choices](#engineering-choices) ·
[Next evidence](#next-evidence-to-collect)

---

## The challenge

Cement operating comparisons can confuse plant size with efficiency and potential savings with
realised value. KILNOMICS keeps workbook inputs, intensive metrics, model evidence and constrained
scenarios visible so a value case can be reviewed before an operational decision.

## System at a glance

```mermaid
flowchart LR
    N0["Workbook validation"]
    N1["Soft-sensor training"]
    N2["Evidence gates"]
    N3["Constrained value case"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
```

## Walk through the project

### 1. Load the workbook

Use the synthetic demo first. The API validates workbook structure and usable data before fitting
or analysis.

### 2. Watch the stages

The background run exposes validation, training and analysis progress. A progress rail is tied to
backend stages, not a simulated loading story.

### 3. Inspect model evidence

Read sample size, input coverage, holdout results and release gates. A model that fails a gate
remains ineligible rather than becoming a recommendation by default.

### 4. Evaluate a scenario

Compare a TSR change against uploaded plant capability and fuel/cost inputs. Keep potential,
validated and finance-realised value as separate states.

## What the pilot does

- Validate workbook coverage, sheets and usable data.
- Fit soft sensors and expose sample size, holdout evidence and model release gates.
- Compare plants using intensive metrics rather than absolute plant scale.
- Evaluate a constrained TSR scenario against uploaded capability, prices and production.
- Show portfolio, plant comparisons, scenarios and evidence/finance views.

```mermaid
flowchart LR
    Workbook[Local XLSX] --> Validate[Data quality]
    Validate --> Train[Soft-sensor fitting]
    Train --> Gate[Evidence gates]
    Gate --> Analysis[Cost and operating analysis]
    Analysis --> UI[React dashboard]
    UI --> Scenario[Constrained scenario]
```

## Run locally

Use Python 3.11+ and Node 20+ as documented for the pilot.

```bash
git clone https://github.com/DanushArun/KILNOMICS.git
cd KILNOMICS
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd frontend
npm ci
cd ..
.venv/bin/uvicorn backend.app.main:app --reload --port 8000
```

In another terminal, from the repository root:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`. The API permits that frontend origin.
Both servers run locally; this pilot does not use a cloud workbook-analysis service.

## Try the synthetic workbook

Download **Demo workbook** in the UI or use
[KILNOMICS_Demo_Data.xlsx](demo/KILNOMICS_Demo_Data.xlsx), then upload it.
The progress rail reflects validation, model fitting and analysis stages.
Review Portfolio, Compare plants, Scenario and Evidence & finance after completion.

Synthetic results demonstrate the software flow. They do not establish actual plant savings,
operational suitability or a causal relationship between measured variables.

## API and repository

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Local pilot health |
| `GET /api/demo-workbook` | Synthetic example workbook |
| `POST /api/workbooks/train` | Synchronous workbook analysis |
| `POST /api/workbooks/train/start` | Start background analysis |
| `GET /api/workbooks/runs/{run_id}` | Read analysis progress/results |
| `POST /api/scenarios` | Evaluate scenario against an analysis |

[backend/app](backend/app) owns chemistry, costs, data quality, training, gates and scenarios.
[frontend/src](frontend/src) owns the dashboard and insights. [AGENT.md](AGENT.md) is the
broader founding brief; it includes intended scope beyond this implemented pilot.

## Verification and limitations

Python behavioral tests are in [tests](tests); frontend checks are declared as:

```bash
cd frontend
npm test
npm run build
```

Source, tests and API contracts were reviewed; the suites and workbook flow were not rerun
for this README update. There is no claim of a new measured pass count.
Analyses are held in process memory and expire on restart, so re-upload before scenario work.
The pilot does not control a kiln. A potential saving needs constrained analysis, plant review
and finance validation before it can be recorded as realised value.

## Engineering choices

**Intensive comparisons.** Cross-plant comparisons avoid treating absolute scale as an efficiency
gap.

**Model eligibility is explicit.** Holdout evidence and gates stay visible to the reviewer.

**Value has distinct states.** A modeled opportunity does not become a finance-realised saving
automatically.

## Implementation state

| State | Current evidence |
| --- | --- |
| Present | Local workbook validation, training and analysis |
| Present | Intensive comparisons and constrained scenario source |
| Present | Synthetic workbook and behavioral test sources |
| Not validated | Real plant savings or autonomous kiln control |

The [architecture guide](docs/ARCHITECTURE.md) maps these statements to source entry points.
The [evaluation guide](docs/EVALUATION.md) separates inspection, executable checks and
domain validation, with the next evidence needed for each project.

## Next evidence to collect

- Record a clean synthetic workbook evaluation.
- Validate domain assumptions with authorized plant evidence.
- Reconcile finance-realised values independently of model potential.
