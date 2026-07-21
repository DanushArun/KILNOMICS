import { ChangeEvent, useMemo, useState } from "react";

import { ExecutiveDashboard } from "./dashboard";
import { hasTrainingEvidence } from "./insights";
import {
  DashboardSummary,
  DataStatus,
  Report,
  TrainingResponse,
  View,
} from "./types";
import { DataReadiness, ModelEvidence, Scenario } from "./views";

const navigation: { view: View; label: string }[] = [
  { view: "dashboard", label: "Dashboard" },
  { view: "models", label: "Model evidence" },
  { view: "scenario", label: "Scenario" },
  { view: "data", label: "Data readiness" },
];

type TrainingSetters = {
  setReports: (reports: Record<string, Report>) => void;
  setSummary: (summary: DashboardSummary) => void;
  setDataStatus: (status: DataStatus) => void;
  setStatus: (message: string) => void;
};

export default function App() {
  const [view, setView] = useState<View>("dashboard");
  const [reports, setReports] = useState<Record<string, Report>>({});
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [dataStatus, setDataStatus] = useState<DataStatus | null>(null);
  const [status, setStatus] = useState(
    "Upload a workbook to start a model run.",
  );
  const [loading, setLoading] = useState(false);
  const [scm, setScm] = useState(29);
  const [tsr, setTsr] = useState(12);
  const annual = useMemo(
    () => estimateAnnualValue(scm, summary),
    [scm, summary],
  );

  async function uploadWorkbook(
    event: ChangeEvent<HTMLInputElement>,
  ): Promise<void> {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setStatus(`Training from ${file.name}…`);
    const body = new FormData();
    body.append("workbook", file);
    try {
      const result = await requestTraining(body);
      applyTraining(result, {
        setReports,
        setSummary,
        setDataStatus,
        setStatus,
      });
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Training failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-canvas">
      <Masthead
        active={view}
        loading={loading}
        onNavigate={setView}
        onUpload={uploadWorkbook}
      />
      <p className="run-status">{status}</p>
      <Content
        annual={annual}
        dataStatus={dataStatus}
        reports={reports}
        scm={scm}
        setScm={setScm}
        setTsr={setTsr}
        summary={summary}
        tsr={tsr}
        view={view}
      />
    </main>
  );
}

async function requestTraining(body: FormData): Promise<TrainingResponse> {
  const response = await fetch("http://localhost:8000/api/workbooks/train", {
    method: "POST",
    body,
  });
  const result = await response.json();
  if (!response.ok || !hasTrainingEvidence(result))
    throw new Error(
      "API is out of date. Restart the backend, then upload again.",
    );
  return result as TrainingResponse;
}

function applyTraining(
  response: TrainingResponse,
  setters: TrainingSetters,
): void {
  setters.setReports(response.reports);
  setters.setSummary(response.summary);
  setters.setDataStatus(response.data_status);
  setters.setStatus(
    `Training complete · ${response.source} · review evidence before acting.`,
  );
}

function estimateAnnualValue(
  scm: number,
  summary: DashboardSummary | null,
): number {
  if (!summary) return 0;
  return (
    (scm - summary.scm_pct) *
    (summary.clinker_cost_per_t - 1500) *
    summary.monthly_volume_t *
    0.12
  );
}

function Masthead({
  active,
  loading,
  onNavigate,
  onUpload,
}: {
  active: View;
  loading: boolean;
  onNavigate: (view: View) => void;
  onUpload: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <header className="masthead">
      <a className="wordmark" href="/">
        KILNOMICS<span>value · quality · energy</span>
      </a>
      <nav className="top-nav">
        {navigation.map((item) => (
          <button
            className={item.view === active ? "selected" : ""}
            key={item.view}
            onClick={() => onNavigate(item.view)}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <div className="header-actions">
        <a
          className="button secondary"
          href="http://localhost:8000/api/demo-workbook"
        >
          Demo workbook
        </a>
        <label className="button primary">
          {loading ? "Training…" : "Upload workbook"}
          <input
            accept=".xlsx"
            disabled={loading}
            onChange={onUpload}
            type="file"
          />
        </label>
      </div>
    </header>
  );
}

function Content({
  annual,
  dataStatus,
  reports,
  scm,
  setScm,
  setTsr,
  summary,
  tsr,
  view,
}: {
  annual: number;
  dataStatus: DataStatus | null;
  reports: Record<string, Report>;
  scm: number;
  setScm: (value: number) => void;
  setTsr: (value: number) => void;
  summary: DashboardSummary | null;
  tsr: number;
  view: View;
}) {
  if (view === "models") return <ModelEvidence reports={reports} />;
  if (view === "scenario")
    return (
      <Scenario
        annual={annual}
        scm={scm}
        setScm={setScm}
        setTsr={setTsr}
        summary={summary}
        tsr={tsr}
      />
    );
  if (view === "data")
    return <DataReadiness dataStatus={dataStatus} reports={reports} />;
  return (
    <ExecutiveDashboard
      dataStatus={dataStatus}
      reports={reports}
      summary={summary}
    />
  );
}
