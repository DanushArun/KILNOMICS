import { formatDateRange, formatFeatureList, formatRupees } from "./insights";
import { DashboardSummary, DataStatus, Report } from "./types";

export function ModelEvidence({
  reports,
}: {
  reports: Record<string, Report>;
}) {
  const rows = Object.values(reports);
  return (
    <section className="detail-view">
      <p className="section-label">Model command centre</p>
      <h1>Can the model be trusted?</h1>
      {rows.length === 0 ? (
        <p>Upload a workbook to generate model evidence.</p>
      ) : (
        <ModelTable rows={rows} />
      )}
    </section>
  );
}

function ModelTable({ rows }: { rows: Report[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Target</th>
          <th>Inputs</th>
          <th>Rows</th>
          <th>Holdout</th>
          <th>R²</th>
          <th>MAE</th>
          <th>Decision</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((report) => (
          <tr key={report.target}>
            <td>{report.target}</td>
            <td title={report.input_features.join(", ")}>
              {formatFeatureList(report.input_features, 3)}
            </td>
            <td>{report.sample_count}</td>
            <td>{report.holdout_count}</td>
            <td>{report.metrics.r_squared.toFixed(2)}</td>
            <td>{report.metrics.mae.toFixed(2)}</td>
            <td>{report.passed ? "Eligible" : "Blocked"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function Scenario({
  annual,
  scm,
  setScm,
  setTsr,
  summary,
  tsr,
}: {
  annual: number;
  scm: number;
  setScm: (value: number) => void;
  setTsr: (value: number) => void;
  summary: DashboardSummary | null;
  tsr: number;
}) {
  return (
    <section className="detail-view scenario-view">
      <p className="section-label">Constrained scenario</p>
      <h1>Test a bounded mix change.</h1>
      <div className="scenario-grid">
        <article className="panel">
          <RangeControl
            label="SCM share"
            max={35}
            min={15}
            onChange={setScm}
            value={scm}
          />
          <RangeControl
            label="Thermal substitution"
            max={16}
            min={0}
            onChange={setTsr}
            value={tsr}
          />
        </article>
        <article className="panel">
          <h2>Current calculation</h2>
          <strong>{summary ? formatRupees(annual) : "Upload workbook"}</strong>
          <p>
            Indicative cost movement only. A firm recommendation requires the
            chemistry and quality solver, which is not yet implemented.
          </p>
        </article>
      </div>
    </section>
  );
}

function RangeControl({
  label,
  max,
  min,
  onChange,
  value,
}: {
  label: string;
  max: number;
  min: number;
  onChange: (value: number) => void;
  value: number;
}) {
  return (
    <label>
      {label} <output>{value}%</output>
      <input
        max={max}
        min={min}
        onChange={(event) => onChange(Number(event.target.value))}
        type="range"
        value={value}
      />
    </label>
  );
}

export function DataReadiness({
  dataStatus,
  reports,
}: {
  dataStatus: DataStatus | null;
  reports: Record<string, Report>;
}) {
  return (
    <section className="detail-view">
      <p className="section-label">Data readiness</p>
      <h1>What entered the model?</h1>
      {!dataStatus ? (
        <p>Upload a workbook to inspect its source sheets and coverage.</p>
      ) : (
        <>
          <p>
            {dataStatus.overall_status} ·{" "}
            {formatDateRange(dataStatus.start_date, dataStatus.end_date)} ·{" "}
            {Object.keys(reports).length} trained targets
          </p>
          <SheetTable sheets={dataStatus.sheets} />
        </>
      )}
    </section>
  );
}

function SheetTable({ sheets }: { sheets: DataStatus["sheets"] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Source sheet</th>
          <th>Rows</th>
          <th>State</th>
        </tr>
      </thead>
      <tbody>
        {sheets.map((sheet) => (
          <tr key={sheet.name}>
            <td>{sheet.name}</td>
            <td>{sheet.row_count}</td>
            <td>{sheet.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
