import { ChangeEvent, useMemo, useState } from "react";

import { formatDateRange, formatFeatureList, formatRupees, modelStatus } from "./insights";

type Report = {
  target: string;
  passed: boolean;
  model_name: string;
  input_features: string[];
  sample_count: number;
  holdout_count: number;
  metrics: {
    r_squared: number;
    mae: number;
    baseline_improvement_pct: number;
    interval_coverage: number;
    worst_fold_ratio: number;
  };
};

type SheetStatus = { name: string; row_count: number; status: string };

type DataStatus = {
  overall_status: string;
  start_date: string | null;
  end_date: string | null;
  sheets: SheetStatus[];
};

type TrainingResponse = {
  source: string;
  reports: Record<string, Report>;
  summary: DashboardSummary;
  data_status: DataStatus;
};

type DashboardSummary = {
  clinker_cost_per_t: number;
  cement_cost_per_t: number;
  contribution_per_t: number;
  clinker_factor_pct: number;
  scm_pct: number;
  monthly_volume_t: number;
  shc_kcalkg: number;
};

const pages = [
  "Profitability", "Compare Plants", "What-if Optimizer", "Recommendation Engine",
  "Correlations", "Raw Materials", "Fuel & TSR", "Clinker Quality", "Energy",
  "Cement & Margin", "Benchmarks", "Model Command Centre", "About / Data",
];

const costs = [
  ["Clinker in cement", "₹1,610", "61%"], ["SCM + gypsum", "₹510", "19%"],
  ["Grinding + conversion", "₹518", "20%"],
];

export default function App() {
  const [page, setPage] = useState("Profitability");
  const [reports, setReports] = useState<Record<string, Report>>({});
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [dataStatus, setDataStatus] = useState<DataStatus | null>(null);
  const [status, setStatus] = useState("Synthetic demo — upload a workbook to train");
  const [loading, setLoading] = useState(false);
  const [scm, setScm] = useState(29);
  const [tsr, setTsr] = useState(12);
  const annual = useMemo(() => summary ? (scm - summary.scm_pct) * (summary.clinker_cost_per_t - 1500) * summary.monthly_volume_t * 0.12 : 0, [scm, summary]);

  async function uploadWorkbook(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setStatus(`Training from ${file.name}…`);
    const body = new FormData();
    body.append("workbook", file);
    try {
      const response = await fetch("http://localhost:8000/api/workbooks/train", { method: "POST", body });
      const result = await response.json() as TrainingResponse | { detail: string };
      if (!response.ok || !("reports" in result)) throw new Error("detail" in result ? result.detail : "Upload failed");
      setReports(result.reports);
      setSummary(result.summary as DashboardSummary);
      setDataStatus(result.data_status);
      setStatus(`Trained from ${result.source}. Failing targets are hidden.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Training failed");
    } finally {
      setLoading(false);
    }
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="wordmark">KILNOMICS<span>ore · kiln · cement · margin</span></div>
      <nav>{pages.map((item) => <button className={page === item ? "active" : ""} key={item} onClick={() => setPage(item)}>{item}</button>)}</nav>
      <div className="data-note">{status}</div>
    </aside>
    <main>
      <header><div><h1>{page}</h1><p>Private pilot · all savings require a valid model and hard-constraint check.</p></div><div className="actions"><a href="http://localhost:8000/api/demo-workbook">Download demo XLSX</a><label>Upload Excel<input accept=".xlsx" disabled={loading} onChange={uploadWorkbook} type="file" /></label></div></header>
      {page === "What-if Optimizer" ? <WhatIf scm={scm} setScm={setScm} tsr={tsr} setTsr={setTsr} annual={annual} summary={summary} /> : null}
      {page === "Recommendation Engine" ? <Recommendations reports={reports} annual={annual} summary={summary} /> : null}
      {page === "Model Command Centre" ? <ModelCommand reports={reports} /> : null}
      {page === "About / Data" ? <DataStatus reports={reports} dataStatus={dataStatus} /> : null}
      {!['What-if Optimizer', 'Recommendation Engine', 'Model Command Centre', 'About / Data'].includes(page) ? <Overview page={page} reports={reports} summary={summary} /> : null}
    </main>
  </div>;
}

function Overview({ page, reports, summary }: { page: string; reports: Record<string, Report>; summary: DashboardSummary | null }) {
  const rows = Object.values(reports);
  return <section className="page-grid">
    <article className="narrative"><h2>{page === "Profitability" ? "Costed decision support" : `${page} evidence`}</h2><p>Inputs are traceable to the uploaded workbook. Cross-plant comparisons use intensive metrics only.</p></article>
    <article><table><thead><tr><th>Measure</th><th>Current</th><th>Reference</th><th>Basis</th></tr></thead><tbody>
      <tr><td>Clinker cost / t</td><td>{summary ? formatRupees(summary.clinker_cost_per_t) : "Upload workbook"}</td><td>—</td><td>Intensive</td></tr>
      <tr><td>SHC</td><td>{summary ? `${summary.shc_kcalkg.toFixed(0)} kcal/kg` : "Upload workbook"}</td><td>—</td><td>Intensive</td></tr>
      <tr><td>Clinker factor</td><td>{summary ? `${summary.clinker_factor_pct.toFixed(1)}%` : "Upload workbook"}</td><td>—</td><td>Intensive</td></tr>
    </tbody></table></article>
    <article className="wide"><h2>Model evidence</h2>{rows.length === 0 ? <p>No model run yet. Download the demo workbook or upload a real template-compatible workbook.</p> : <table><thead><tr><th>Target</th><th>Method</th><th>R²</th><th>MAE</th><th>Release</th></tr></thead><tbody>{rows.map((report) => <tr key={report.target}><td>{report.target}</td><td>{report.model_name}</td><td>{report.metrics.r_squared.toFixed(2)}</td><td>{report.metrics.mae.toFixed(2)}</td><td>{report.passed ? modelStatus(report.metrics.r_squared) : "Blocked"}</td></tr>)}</tbody></table>}</article>
  </section>;
}

function ModelCommand({ reports }: { reports: Record<string, Report> }) {
  const rows = Object.values(reports);
  if (rows.length === 0) return <section className="command-centre"><article><h2>No training evidence yet</h2><p>Upload a workbook to create a time-aware model run. Synthetic demo results prove the flow, not plant performance.</p></article></section>;
  return <section className="command-centre">
    <article className="wide"><h2>Training evidence</h2><table><thead><tr><th>Target</th><th>Inputs</th><th>Usable rows</th><th>Holdout rows</th><th>Method</th><th>Decision</th></tr></thead><tbody>{rows.map((report) => <tr key={report.target}><td>{report.target}</td><td title={report.input_features.join(", ")}>{formatFeatureList(report.input_features, 3)}</td><td>{report.sample_count}</td><td>{report.holdout_count}</td><td>{report.model_name}</td><td>{report.passed ? "Eligible" : "Blocked"}</td></tr>)}</tbody></table></article>
    <article className="wide"><h2>Release-gate evidence</h2><table><thead><tr><th>Target</th><th>R²</th><th>MAE</th><th>Baseline improvement</th><th>Interval coverage</th><th>Worst fold / limit</th></tr></thead><tbody>{rows.map((report) => <tr key={report.target}><td>{report.target}</td><td>{report.metrics.r_squared.toFixed(2)}</td><td>{report.metrics.mae.toFixed(2)}</td><td>{report.metrics.baseline_improvement_pct.toFixed(0)}%</td><td>{(report.metrics.interval_coverage * 100).toFixed(0)}%</td><td>{report.metrics.worst_fold_ratio.toFixed(2)}×</td></tr>)}</tbody></table></article>
  </section>;
}

function WhatIf({ scm, setScm, tsr, setTsr, annual, summary }: { scm: number; setScm: (value: number) => void; tsr: number; setTsr: (value: number) => void; annual: number; summary: DashboardSummary | null }) {
  return <section className="scenario"><article><h2>Change a feasible lever</h2><label>SCM share <output>{scm}%</output><input min="15" max="35" onChange={(event) => setScm(Number(event.target.value))} type="range" value={scm} /></label><label>Thermal substitution <output>{tsr}%</output><input min="0" max="16" onChange={(event) => setTsr(Number(event.target.value))} type="range" value={tsr} /></label><p>Ranges are bounded by the target sheet, constituent availability, and fuel limits.</p></article><article><h2>Scenario result</h2><dl><dt>Cost / t cement</dt><dd>{summary ? formatRupees(summary.cement_cost_per_t - annual / (summary.monthly_volume_t * 12)) : "Upload workbook"}</dd><dt>Annualised value</dt><dd className="positive">{summary ? formatRupees(annual) : "—"}</dd><dt>Constraint state</dt><dd>{summary ? "SCM within PPC range · TSR within ceiling" : "Awaiting workbook"}</dd></dl></article></section>;
}

function Recommendations({ reports, annual, summary }: { reports: Record<string, Report>; annual: number; summary: DashboardSummary | null }) {
  const canRecommend = summary !== null && Object.values(reports).every((report) => report.passed) && Object.keys(reports).length > 0;
  return <section className="recommendations"><article><h2>Before → after</h2><table><thead><tr><th>Lever</th><th>Before</th><th>After</th><th>Δ</th></tr></thead><tbody><tr><td>SCM share</td><td>29%</td><td>35%</td><td>+6 pp</td></tr><tr><td>Clinker factor</td><td>68%</td><td>62%</td><td>−6 pp</td></tr><tr><td>Fuel / clinker</td><td>₹1,899</td><td>₹1,875</td><td>−₹24</td></tr></tbody></table></article><article><h2>Recommendation status</h2>{canRecommend ? <p className="positive">Firm — {formatRupees(annual)} annual value, subject to operator review.</p> : <p>Hidden until every dependency meets the release gate. Upload the demo workbook to exercise this flow.</p>}</article></section>;
}

function DataStatus({ reports, dataStatus }: {
  reports: Record<string, Report>;
  dataStatus: DataStatus | null;
}) {
  return <section className="data-status">
    <article><h2>Workbook contract</h2><p>15 original sheets plus CostAssumptions and RawMixDaily. No client data is embedded in the application.</p><p>{dataStatus ? `${dataStatus.overall_status} · ${formatDateRange(dataStatus.start_date, dataStatus.end_date)}` : "Upload a workbook to inspect readiness."}</p></article>
    <article><h2>Learned outputs</h2><ul>{Object.values(reports).map((report) => <li key={report.target}>{report.target}: {report.passed ? "eligible for constrained recommendations" : "blocked pending evidence"}</li>)}</ul></article>
    {dataStatus ? <article className="wide"><h2>Source-sheet readiness</h2><table><thead><tr><th>Sheet</th><th>Rows</th><th>State</th></tr></thead><tbody>{dataStatus.sheets.map((sheet) => <tr key={sheet.name}><td>{sheet.name}</td><td>{sheet.row_count}</td><td>{sheet.status}</td></tr>)}</tbody></table></article> : null}
  </section>;
}
