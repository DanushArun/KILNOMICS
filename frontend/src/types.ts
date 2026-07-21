export type Metric = {
  r_squared: number;
  mae: number;
  baseline_improvement_pct: number;
  interval_coverage: number;
  worst_fold_ratio: number;
};

export type Report = {
  target: string;
  passed: boolean;
  model_name: string;
  input_features: string[];
  sample_count: number;
  holdout_count: number;
  metrics: Metric;
};

export type SheetStatus = { name: string; row_count: number; status: string };

export type DataStatus = {
  overall_status: string;
  start_date: string | null;
  end_date: string | null;
  sheets: SheetStatus[];
};

export type Point = { date: string; value: number };

export type DashboardSummary = {
  clinker_cost_per_t: number;
  cement_cost_per_t: number;
  contribution_per_t: number;
  clinker_factor_pct: number;
  scm_pct: number;
  monthly_volume_t: number;
  shc_kcalkg: number;
  shc_series: Point[];
};

export type Plant = {
  plant_id: string;
  plant_name: string;
  rated_clinker_tpd: number;
  structure: string;
  clinker_cost_per_t: number;
  cement_cost_per_t: number;
  contribution_per_t: number;
  monthly_volume_t: number;
  shc_kcalkg: number;
  tsr_pct: number;
  clinker_factor_pct: number;
  false_air_pct: number;
  limits: { tsr_max_pct: number; scm_min_pct: number; scm_max_pct: number };
};

export type Opportunity = {
  id: string;
  plant_id: string;
  plant_name: string;
  lever: string;
  metric: string;
  baseline: number;
  target: number;
  savings_per_t: number;
  annual_savings_rs: number;
  confidence: string;
  state: string;
};

export type Benchmark = {
  plant_id: string;
  metric: string;
  value: number;
  gap_to_best: number;
};

export type ScenarioConstraint = {
  name: string;
  state: "pass" | "blocked";
  message: string;
};

export type ScenarioResult = {
  feasible: boolean;
  annual_savings_rs: number;
  savings_per_t: number;
  constraints: ScenarioConstraint[];
};

export type Portfolio = {
  annual_savings_rs: number;
  practical_annual_savings_rs: number;
  opportunity_count: number;
};

export type Provenance = { mode: string; label: string; disclaimer: string };

export type FinanceStatus = { state: string; realised_annual_rs: number };

export type TrainingResponse = {
  source: string;
  reports: Record<string, Report>;
  summary: DashboardSummary;
  data_status: DataStatus;
  analysis_id: string;
  portfolio: Portfolio;
  plants: Plant[];
  benchmarks: Benchmark[];
  opportunities: Opportunity[];
  provenance: Provenance;
  finance_status: FinanceStatus;
};

export type TrainingRun = {
  run_id: string;
  phase: "queued" | "validating" | "training" | "analysing" | "complete" | "failed";
  progress_pct: number;
  result: TrainingResponse | null;
  error: string | null;
};

export type View = "portfolio" | "compare" | "actions" | "scenario" | "evidence";
