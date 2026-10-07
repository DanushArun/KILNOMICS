# KILNOMICS — Evaluation guide

Start with the smallest path that exercises the project. Distinguish source inspection,
syntax/build checks, functional behavior and domain validation when recording a result.

## Guided reading and demonstration

1. **Load the workbook.** Use the synthetic demo first. The API validates workbook structure and
usable data before fitting or analysis.

2. **Watch the stages.** The background run exposes validation, training and analysis progress. A
progress rail is tied to backend stages, not a simulated loading story.

3. **Inspect model evidence.** Read sample size, input coverage, holdout results and release
gates. A model that fails a gate remains ineligible rather than becoming a recommendation by
default.

4. **Evaluate a scenario.** Compare a TSR change against uploaded plant capability and fuel/cost
inputs. Keep potential, validated and finance-realised value as separate states.

## Declared checks

These commands/checks describe the intended verification path. Their presence in this
guide does not claim that they passed. See the dated evidence below and the README for setup.

```text
python -m pytest -q tests
cd frontend && npm test
cd frontend && npm run build
```

## Evidence levels

| Level | What it establishes | What it does not establish |
| --- | --- | --- |
| Source review | A path exists in tracked code | Successful runtime behavior |
| Syntax/build | Parser/compiler accepts that path | End-to-end correctness |
| Behavioral check | A specific input/output case passed | Generalization beyond cases |
| Domain evaluation | Performance on a stated target setting | Other users/data/environments |

## What to record

- Commit, environment, dependency versions and date.
- Input provenance and whether data is synthetic, public or privately supplied.
- Absolute pass/fail/skip counts; keep failed cases and their root causes.
- Whether external services, hardware or a production deployment were actually exercised.
- Expected output and an artifact showing the observation.

## Review scenarios

- **Intensive comparisons:** Cross-plant comparisons avoid treating absolute scale as an
efficiency gap.

- **Model eligibility is explicit:** Holdout evidence and gates stay visible to the reviewer.

- **Value has distinct states:** A modeled opportunity does not become a finance-realised saving
automatically.

## Documentation inspection — 7 October 2026

The documentation was traced to committed source and checked for local links, balanced
code fences and supported implementation claims. Historical notebook outputs remain labeled
as historical. Live provider access, private databases and hardware behavior are not inferred
from configuration or dependency files. Any fresh run is recorded separately in the README.

## Next evidence to collect

- Record a clean synthetic workbook evaluation.
- Validate domain assumptions with authorized plant evidence.
- Reconcile finance-realised values independently of model potential.
