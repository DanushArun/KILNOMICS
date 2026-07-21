import { buildLinePath, formatDateRange, formatRupees } from "./insights";
import { DashboardSummary, DataStatus, Point, Report } from "./types";

export function ExecutiveDashboard({
  dataStatus,
  reports,
  summary,
}: {
  dataStatus: DataStatus | null;
  reports: Record<string, Report>;
  summary: DashboardSummary | null;
}) {
  if (!summary) return <AwaitingWorkbook />;
  const eligible = Object.values(reports).filter(
    (report) => report.passed,
  ).length;
  return (
    <section className="dashboard">
      <DashboardHeading />
      <MetricRow summary={summary} />
      <section className="feature-grid">
        <PerformancePanel series={summary.shc_series} />
        <EvidencePanel eligible={eligible} reports={reports} />
      </section>
      <section className="lower-grid">
        <EconomicsPanel summary={summary} />
        <DecisionPanel dataStatus={dataStatus} eligible={eligible} />
      </section>
    </section>
  );
}

function DashboardHeading() {
  return (
    <section className="dashboard-heading">
      <div>
        <p className="section-label">Executive decision support</p>
        <h1>Clinker-to-cement value view</h1>
      </div>
      <p>
        Every number is derived from the uploaded workbook. Savings remain
        unavailable until a constrained scenario is solved.
      </p>
    </section>
  );
}

function MetricRow({ summary }: { summary: DashboardSummary }) {
  return (
    <section className="metric-row">
      <Metric
        label="Contribution margin"
        value={`${formatRupees(summary.contribution_per_t)} / t`}
      />
      <Metric
        label="Clinker cost"
        value={`${formatRupees(summary.clinker_cost_per_t)} / t`}
      />
      <Metric
        label="Specific heat consumption"
        value={`${summary.shc_kcalkg.toFixed(0)} kcal/kg`}
      />
    </section>
  );
}

function AwaitingWorkbook() {
  return (
    <section className="awaiting-workbook">
      <p className="section-label">Private local pilot</p>
      <h1>Upload the plant workbook to create the decision view.</h1>
      <p>
        The dashboard will then show source readiness, model performance, daily
        SHC behaviour, and the economics needed for a constrained scenario.
      </p>
      <ol>
        <li>Download the template or open the supplied demo workbook.</li>
        <li>Upload a valid `.xlsx` file.</li>
        <li>Review the evidence before considering an operating action.</li>
      </ol>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <article className="metric">
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}

function PerformancePanel({ series }: { series: Point[] }) {
  const values = series.map((point) => point.value);
  const path = buildLinePath(values, 620, 180);
  const first = series[0]?.date;
  const last = series.at(-1)?.date;
  return (
    <article className="panel performance">
      <div className="panel-heading">
        <div>
          <h2>Specific heat consumption</h2>
          <p>{formatDateRange(first ?? null, last ?? null)} · daily average</p>
        </div>
        <strong>
          {Math.min(...values).toFixed(0)}–{Math.max(...values).toFixed(0)}{" "}
          kcal/kg
        </strong>
      </div>
      <svg
        aria-label="Daily specific heat consumption"
        role="img"
        viewBox="0 0 620 180"
      >
        <path
          className="gridline"
          d="M 0 45 H 620 M 0 90 H 620 M 0 135 H 620"
        />
        <path className="trend" d={path} />
      </svg>
      <div className="chart-labels">
        <span>{first}</span>
        <span>{last}</span>
      </div>
    </article>
  );
}

function EvidencePanel({
  eligible,
  reports,
}: {
  eligible: number;
  reports: Record<string, Report>;
}) {
  const rows = Object.values(reports);
  return (
    <article className="panel evidence">
      <div className="panel-heading">
        <div>
          <h2>Model evidence</h2>
          <p>Chronological holdout gate</p>
        </div>
        <strong>
          {eligible}/{rows.length || 4}
        </strong>
      </div>
      {rows.length === 0 ? (
        <p>No model run available.</p>
      ) : (
        <ul className="model-list">
          {rows.map((report) => (
            <li key={report.target}>
              <span>{report.target}</span>
              <span>R² {report.metrics.r_squared.toFixed(2)}</span>
              <b className={report.passed ? "pass" : "block"}>
                {report.passed ? "Eligible" : "Blocked"}
              </b>
            </li>
          ))}
        </ul>
      )}
      <button className="text-button">Open model evidence →</button>
    </article>
  );
}

function EconomicsPanel({ summary }: { summary: DashboardSummary }) {
  return (
    <article className="panel economics">
      <h2>Economics at current recipe</h2>
      <dl>
        <div>
          <dt>Cement cost</dt>
          <dd>{formatRupees(summary.cement_cost_per_t)} / t</dd>
        </div>
        <div>
          <dt>Clinker factor</dt>
          <dd>{summary.clinker_factor_pct.toFixed(1)}%</dd>
        </div>
        <div>
          <dt>SCM share</dt>
          <dd>{summary.scm_pct.toFixed(1)}%</dd>
        </div>
      </dl>
      <p>
        Cost and margin values are workbook-derived; they are not benchmark
        claims.
      </p>
    </article>
  );
}

function DecisionPanel({
  dataStatus,
  eligible,
}: {
  dataStatus: DataStatus | null;
  eligible: number;
}) {
  return (
    <article className="panel decision">
      <h2>Decision gate</h2>
      <strong>
        {dataStatus?.overall_status === "ready" ? "Data ready" : "Data pending"}
      </strong>
      <p>
        {eligible} model{eligible === 1 ? "" : "s"} pass the evidence gate. The
        system still requires hard chemistry, quality, and capability checks
        before showing a saving.
      </p>
      <button className="text-button">Review readiness →</button>
    </article>
  );
}
