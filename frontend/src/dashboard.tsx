import { formatRupees, valuePoolByLever } from "./insights";
import { Opportunity, TrainingResponse, TrainingRun } from "./types";

export function PortfolioDashboard({ analysis }: { analysis: TrainingResponse }) {
  const topActions = [...analysis.opportunities]
    .sort((left, right) => right.annual_savings_rs - left.annual_savings_rs)
    .slice(0, 3);
  return (
    <section className="portfolio-view">
      <header className="page-header">
        <div>
          <h1>Portfolio opportunity</h1>
          <p>{analysis.provenance.disclaimer}</p>
        </div>
        <span className="source-state">{analysis.provenance.label}</span>
      </header>
      <section className="value-summary" aria-label="Illustrative value summary">
        <div>
          <span>Illustrative annual opportunity</span>
          <strong>{formatRupees(analysis.portfolio.annual_savings_rs)}</strong>
          <p>
            Practical capture case {formatRupees(analysis.portfolio.practical_annual_savings_rs)}
          </p>
        </div>
        <dl>
          <ValueRow label="Plants" value={String(analysis.plants.length)} />
          <ValueRow label="Actions" value={String(analysis.portfolio.opportunity_count)} />
          <ValueRow label="Finance-realised" value={formatRupees(analysis.finance_status.realised_annual_rs)} />
        </dl>
      </section>
      <section className="content-grid">
        <article className="table-section">
          <h2>Costed value pool</h2>
          <ValuePoolChart opportunities={analysis.opportunities} />
        </article>
        <article className="action-section">
          <h2>Required decisions</h2>
          <ol className="action-list">
            {topActions.map((action) => <ActionRow action={action} key={action.id} />)}
          </ol>
        </article>
      </section>
      <section className="table-section portfolio-position">
        <h2>Intensive operating position</h2>
        <PlantTable analysis={analysis} />
      </section>
    </section>
  );
}

function ValueRow({ label, value }: { label: string; value: string }) {
  return <div><dt>{label}</dt><dd>{value}</dd></div>;
}

export function PlantTable({ analysis }: { analysis: TrainingResponse }) {
  return (
    <table>
      <thead><tr><th>Plant</th><th>Structure</th><th>Cement cost</th><th>SHC</th><th>TSR</th><th>Clinker factor</th></tr></thead>
      <tbody>
        {analysis.plants.map((plant) => (
          <tr key={plant.plant_id}>
            <td><strong>{plant.plant_name}</strong><br /><span>{plant.rated_clinker_tpd.toLocaleString("en-IN")} tpd</span></td>
            <td>{plant.structure}</td>
            <td>{formatRupees(plant.cement_cost_per_t)} / t</td>
            <td>{plant.shc_kcalkg.toFixed(0)} kcal/kg</td>
            <td>{plant.tsr_pct.toFixed(1)}%</td>
            <td>{plant.clinker_factor_pct.toFixed(1)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function ActionRow({ action }: { action: Opportunity }) {
  return (
    <li>
      <div><strong>{action.lever}</strong><span>{action.plant_name}</span></div>
      <div><strong>{formatRupees(action.annual_savings_rs)}</strong><span>{formatRupees(action.savings_per_t)} / t</span></div>
    </li>
  );
}

export function AwaitingWorkbook() {
  return (
    <section className="awaiting-workbook">
      <h1>Upload a plant workbook</h1>
      <p>Use the demo workbook for the fictional three-plant value case, or upload a client workbook for unverified analysis.</p>
    </section>
  );
}

export function TrainingProgress({ run }: { run: TrainingRun }) {
  const label = progressLabel(run.phase);
  return (
    <section className="training-progress" aria-live="polite">
      <div><h2>{label}</h2><p>Analysis status updates as each validation and model-evidence stage completes.</p></div>
      <strong>{run.progress_pct}%</strong>
      <div className="progress-track" role="progressbar" aria-valuemax={100}
        aria-valuemin={0} aria-valuenow={run.progress_pct}><span style={{ width: `${run.progress_pct}%` }} /></div>
      <ol><li className={stageState(run, "validating")}>Validate workbook</li><li className={stageState(run, "training")}>Fit soft sensors</li><li className={stageState(run, "analysing")}>Build value case</li></ol>
    </section>
  );
}

function ValuePoolChart({ opportunities }: { opportunities: Opportunity[] }) {
  const values = valuePoolByLever(opportunities);
  const maximum = values[0]?.value ?? 1;
  return <div className="value-pool">{values.map((item) => <div className="pool-row" key={item.label}><span>{item.label}</span><div className="pool-bar"><i style={{ width: `${(item.value / maximum) * 100}%` }} /></div><strong>{formatRupees(item.value)}</strong></div>)}</div>;
}

function progressLabel(phase: TrainingRun["phase"]): string {
  const labels: Record<TrainingRun["phase"], string> = {
    queued: "Workbook queued", validating: "Validating source data", training: "Fitting soft sensors",
    analysing: "Calculating constrained value", complete: "Analysis complete", failed: "Analysis failed",
  };
  return labels[phase];
}

function stageState(run: TrainingRun, phase: TrainingRun["phase"]): string {
  const order = ["queued", "validating", "training", "analysing", "complete"];
  return order.indexOf(run.phase) >= order.indexOf(phase) ? "complete" : "pending";
}
