# KILNOMICS — Client-Grade ML Decision Support

## Objective

Build a local, private decision-support product for clinker-to-cement cost,
quality, and energy optimisation. It must turn an uploaded plant workbook into
traceable, constraint-aware opportunities, not unaudited predictions.

The long-term ambition is a ₹500 crore value-creation portfolio. The product
must never present that ambition as a model-generated or realised saving.

## Non-negotiable evidence chain

1. **Data ready** — source sheets, coverage, completeness, exclusions, and
   time alignment are visible.
2. **Model credible** — each target exposes its inputs, chronological holdout,
   R², MAE, baseline improvement, uncertainty coverage, residuals, and release
   decision.
3. **Scenario feasible** — chemistry, quality, equipment, fuel, and recipe
   constraints pass before an action is shown.
4. **Value calculable** — ₹/t and annual range expose their assumptions and
   cost basis.
5. **Value realised** — a finance-approved baseline, owner, and actual result
   distinguish realised value from a hypothesis.

## Scope and decision rights

### In scope for v1

- Excel validation and data-status reporting.
- Grey-box chemistry calculations and trained soft sensors.
- Model Command Centre with complete training evidence.
- Intensive-only plant benchmarking.
- Constrained what-if scenarios and ranked, costed recommendations.
- Explicit labels for synthetic, real, partial, failed, and unavailable data.

### Explicitly not in scope for v1

- Autonomous kiln control.
- Causal claims from correlations.
- Unverified ₹500 crore savings claims.
- Liquid phase/coating, SO3 optimum, durability, and full Pareto optimisation.

## Delivery sequence

### 1. Evidence foundation — active

Create a durable training-run contract. The API and dashboard must state what
was ingested, which features trained each target, data volume and holdout span,
all release-gate results, and the reason for any block.

**Acceptance:** a user can upload a workbook and answer: “what trained, on
which data, how well did it perform, and can it be used for a recommendation?”

### 2. Data-readiness and lineage

Validate required sheets, required columns, usable rows, unit/range checks,
duplicates, date coverage, and missingness. Preserve source and run IDs.

### 3. Model Command Centre

Show per-target model cards, actual-versus-predicted evidence, residuals over
time, feature list, uncertainty, baseline comparison, and release decision.

### 4. Constrained value engine

Replace display-only sliders with calculations that solve a bounded scenario,
show every quality/capability check, and calculate a transparent ₹/t waterfall.

### 5. Value-realisation operating cadence

Track potential, validated, and realised value separately. Finance owns the
baseline; plant teams own the operational action.

## Model release policy

A model is recommendation-eligible only when it has chronological holdout
evidence and meets all of the following:

- R² ≥ 0.80.
- Target-specific MAE: strength ≤ 1 MPa, fCaO ≤ 0.20 percentage points,
  C3S ≤ 2 percentage points, SHC ≤ 10 kcal/kg.
- At least 15% MAE improvement over a last-observation baseline.
- 85–95% prediction-interval coverage.
- No holdout fold exceeds the agreed MAE limit.

Synthetic demonstration results are training-flow demonstrations only and can
never populate executive value claims.

## User experience

- **Executive view:** value pool, validated value, realised value, top actions,
  risks, and required decisions.
- **Plant view:** constrained actions, process/quality trade-offs, trends, and
  named owners.
- **Model Command Centre:** data lineage, model evidence, feature inputs,
  error analysis, uncertainty, and run history.

The visual language is restrained and editorial. It must make evidence easier
to read, not make an unsupported claim look premium.

## Research record

Checked 2026-07-21/22.

- [Kami](https://github.com/tw93/Kami): use its restrained editorial hierarchy
  as visual inspiration only; it does not define analytics or governance.
- [IBM machine learning overview](https://www.ibm.com/think/topics/machine-learning):
  validation and monitoring are necessary for models to generalise beyond their
  training data.
- [scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html):
  chronological splitting with a gap is appropriate for time-ordered evidence.
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework): model
  trustworthiness must be managed through design, evaluation, and operation.
- [ThingsBoard](https://github.com/thingsboard/thingsboard): use its asset,
  telemetry, rule-state, and alarm-workflow ideas as architecture inspiration;
  reject its generic SCADA interface and full IoT-platform scope for v1.

**Decision:** build transparent, grey-box decision support rather than a
black-box optimiser or autonomous controller. Confidence: high for the
governance pattern; real performance remains unknown until client workbook
data is validated and back-tested.
