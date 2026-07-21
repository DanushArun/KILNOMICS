import { ActionRow, PlantTable } from "./dashboard";
import { formatFeatureList, formatRupees } from "./insights";
import { ScenarioResult, TrainingResponse } from "./types";

export function PlantComparison({ analysis }: { analysis: TrainingResponse }) {
  return (
    <section className="detail-view">
      <header className="page-header"><div><h1>Compare plants</h1><p>Only intensive metrics are compared. Structural differences remain visible.</p></div></header>
      <PlantTable analysis={analysis} />
      <table className="benchmark-table">
        <thead><tr><th>Plant</th><th>Metric</th><th>Current value</th><th>Gap to portfolio best</th></tr></thead>
        <tbody>{analysis.benchmarks.map((item) => <tr key={item.plant_id}><td>{item.plant_id.replace("DEMO_", "")}</td><td>{item.metric}</td><td>{item.value.toFixed(1)} kcal/kg</td><td>{item.gap_to_best.toFixed(1)} kcal/kg</td></tr>)}</tbody>
      </table>
    </section>
  );
}

export function OpportunityRegister({ analysis }: { analysis: TrainingResponse }) {
  const actions = [...analysis.opportunities].sort((left, right) => right.annual_savings_rs - left.annual_savings_rs);
  return (
    <section className="detail-view">
      <header className="page-header"><div><h1>Opportunity register</h1><p>Illustrative operating actions, ranked by annual value.</p></div></header>
      <ol className="opportunity-register">{actions.map((action) => <ActionRow action={action} key={action.id} />)}</ol>
    </section>
  );
}

export function ScenarioWorkbench({
  analysis, onChange, onRun, result, tsr, running,
}: {
  analysis: TrainingResponse; onChange: (value: number) => void; onRun: () => void;
  result: ScenarioResult | null; tsr: number; running: boolean;
}) {
  const plant = analysis.plants[0];
  return (
    <section className="detail-view">
      <header className="page-header"><div><h1>Scenario workbench</h1><p>Test thermal substitution at {plant.plant_name}; constraints are evaluated by the backend.</p></div></header>
      <section className="scenario-layout">
        <form className="scenario-controls" onSubmit={(event) => { event.preventDefault(); onRun(); }}>
          <label htmlFor="tsr">Thermal substitution target <output>{tsr.toFixed(0)}%</output></label>
          <input id="tsr" max={plant.limits.tsr_max_pct} min={plant.tsr_pct}
            onChange={(event) => onChange(Number(event.target.value))} type="range" value={tsr} />
          <p>Current TSR: {plant.tsr_pct.toFixed(1)}% · capability: {plant.limits.tsr_max_pct}%</p>
          <button className="button primary" disabled={running} type="submit">{running ? "Evaluating…" : "Evaluate scenario"}</button>
        </form>
        <ScenarioResultPanel result={result} />
      </section>
    </section>
  );
}

function ScenarioResultPanel({ result }: { result: ScenarioResult | null }) {
  if (!result) return <article className="scenario-result"><h2>Run a scenario</h2><p>The result will show a data-sourced cost basis only after constraint checks.</p></article>;
  return (
    <article className="scenario-result">
      <h2>{result.feasible ? "Feasible scenario" : "Scenario blocked"}</h2>
      <strong>{formatRupees(result.annual_savings_rs)} / year</strong>
      <p>{formatRupees(result.savings_per_t)} / t cement from uploaded fuel prices,
        heat rate, and volume.</p>
      <ul>{result.constraints.map((item) => <li className={item.state} key={item.name}><strong>{item.name}</strong> {item.message}</li>)}</ul>
    </article>
  );
}

export function EvidenceView({ analysis }: { analysis: TrainingResponse }) {
  const rows = Object.values(analysis.reports);
  return (
    <section className="detail-view">
      <header className="page-header"><div><h1>Evidence and finance</h1><p>{analysis.provenance.disclaimer}</p></div></header>
      <section className="evidence-summary"><strong>{formatRupees(analysis.finance_status.realised_annual_rs)}</strong><span>Finance-realised value</span></section>
      <table>
        <thead><tr><th>Target</th><th>Inputs</th><th>Rows</th><th>R²</th><th>MAE</th><th>Decision</th></tr></thead>
        <tbody>{rows.map((report) => <tr key={report.target}><td>{report.target}</td><td>{formatFeatureList(report.input_features, 3)}</td><td>{report.sample_count}</td><td>{report.metrics.r_squared.toFixed(2)}</td><td>{report.metrics.mae.toFixed(2)}</td><td>{report.passed ? "Model eligible" : "Investigate"}</td></tr>)}</tbody>
      </table>
    </section>
  );
}
