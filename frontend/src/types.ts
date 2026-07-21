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

export type TrainingResponse = {
  source: string;
  reports: Record<string, Report>;
  summary: DashboardSummary;
  data_status: DataStatus;
};

export type View = "dashboard" | "models" | "scenario" | "data";
