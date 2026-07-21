import { ChangeEvent, useState } from "react";

import { AwaitingWorkbook, PortfolioDashboard, TrainingProgress } from "./dashboard";
import { hasPortfolioAnalysis, suggestedTsrTarget } from "./insights";
import { EvidenceView, OpportunityRegister, PlantComparison, ScenarioWorkbench } from "./views";
import { ScenarioResult, TrainingResponse, TrainingRun, View } from "./types";

const navigation: { view: View; label: string }[] = [
  { view: "portfolio", label: "Portfolio" },
  { view: "compare", label: "Compare plants" },
  { view: "actions", label: "Opportunities" },
  { view: "scenario", label: "Scenario" },
  { view: "evidence", label: "Evidence & finance" },
];

export default function App() {
  const [analysis, setAnalysis] = useState<TrainingResponse | null>(null);
  const [view, setView] = useState<View>("portfolio");
  const [status, setStatus] = useState("Upload a workbook to start analysis.");
  const [loading, setLoading] = useState(false);
  const [run, setRun] = useState<TrainingRun | null>(null);
  const [runningScenario, setRunningScenario] = useState(false);
  const [scenario, setScenario] = useState<ScenarioResult | null>(null);
  const [tsr, setTsr] = useState(12);

  async function uploadWorkbook(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setStatus(`Analysing ${file.name}…`);
    const body = new FormData();
    body.append("workbook", file);
    try {
      const result = await requestTraining(body, setRun);
      setAnalysis(result);
      const firstPlant = result.plants[0];
      setTsr(firstPlant ? suggestedTsrTarget(firstPlant.tsr_pct, firstPlant.limits.tsr_max_pct) : 12);
      setScenario(null);
      setStatus(`${result.provenance.label} ready · review opportunity and evidence.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  async function evaluateScenario(): Promise<void> {
    const plant = analysis?.plants[0];
    if (!analysis || !plant) return;
    setRunningScenario(true);
    try {
      const result = await requestScenario(analysis.analysis_id, plant.plant_id, tsr);
      setScenario(result);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Scenario evaluation failed");
    } finally {
      setRunningScenario(false);
    }
  }

  return (
    <main className="app-canvas">
      <Masthead active={view} loading={loading} onNavigate={setView} onUpload={uploadWorkbook} />
      <p className="run-status">{status}</p>
      <Content analysis={analysis} onScenarioChange={setTsr} onScenarioRun={evaluateScenario}
        run={run} scenario={scenario} scenarioRunning={runningScenario} tsr={tsr} view={view} />
    </main>
  );
}

async function requestTraining(
  body: FormData,
  setRun: (run: TrainingRun) => void,
): Promise<TrainingResponse> {
  const response = await fetch("http://localhost:8000/api/workbooks/train/start", {
    method: "POST",
    body,
  });
  const result = await response.json();
  if (!response.ok || typeof result.run_id !== "string") {
    throw new Error(result.detail ?? "Could not start workbook analysis.");
  }
  return waitForTraining(result.run_id, setRun);
}

async function waitForTraining(
  runId: string,
  setRun: (run: TrainingRun) => void,
): Promise<TrainingResponse> {
  const response = await fetch(`http://localhost:8000/api/workbooks/runs/${runId}`);
  const run = await response.json() as TrainingRun;
  if (!response.ok) throw new Error(run.error ?? "Could not read workbook progress.");
  setRun(run);
  if (run.phase === "failed") throw new Error(run.error ?? "Analysis failed.");
  if (run.phase === "complete" && hasPortfolioAnalysis(run.result)) return run.result;
  await new Promise<void>((resolve) => window.setTimeout(resolve, 400));
  return waitForTraining(runId, setRun);
}

async function requestScenario(analysisId: string, plantId: string, tsr: number): Promise<ScenarioResult> {
  const response = await fetch("http://localhost:8000/api/scenarios", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ analysis_id: analysisId, plant_id: plantId, inputs: { tsr_pct: tsr } }),
  });
  const result = await response.json();
  if (!response.ok || !("feasible" in result)) throw new Error(result.detail ?? "Scenario evaluation failed");
  return result as ScenarioResult;
}

function Masthead({ active, loading, onNavigate, onUpload }: {
  active: View; loading: boolean; onNavigate: (view: View) => void; onUpload: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <header className="masthead">
      <a className="wordmark" href="/">KILNOMICS<span>value · quality · energy</span></a>
      <nav className="top-nav">{navigation.map((item) => <button className={item.view === active ? "selected" : ""} key={item.view} onClick={() => onNavigate(item.view)}>{item.label}</button>)}</nav>
      <div className="header-actions"><a className="button secondary" href="http://localhost:8000/api/demo-workbook">Demo workbook</a><label className="button primary">{loading ? "Analysing…" : "Upload workbook"}<input accept=".xlsx" disabled={loading} onChange={onUpload} type="file" /></label></div>
    </header>
  );
}

function Content({ analysis, onScenarioChange, onScenarioRun, run, scenario, scenarioRunning, tsr, view }: {
  analysis: TrainingResponse | null; onScenarioChange: (value: number) => void; onScenarioRun: () => void;
  run: TrainingRun | null; scenario: ScenarioResult | null; scenarioRunning: boolean; tsr: number; view: View;
}) {
  if (!analysis) return <><AwaitingWorkbook />{run && <TrainingProgress run={run} />}</>;
  if (view === "compare") return <PlantComparison analysis={analysis} />;
  if (view === "actions") return <OpportunityRegister analysis={analysis} />;
  if (view === "scenario") return <ScenarioWorkbench analysis={analysis} onChange={onScenarioChange} onRun={onScenarioRun} result={scenario} running={scenarioRunning} tsr={tsr} />;
  if (view === "evidence") return <EvidenceView analysis={analysis} />;
  return <PortfolioDashboard analysis={analysis} />;
}
