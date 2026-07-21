export function formatRupees(value: number): string {
  if (Math.abs(value) >= 10_000_000) {
    return `₹${(value / 10_000_000).toFixed(2)} Cr`;
  }
  return `₹${Math.round(value).toLocaleString("en-IN")}`;
}

export function modelStatus(value: number): string {
  return value >= 0.8 ? "Validated" : "Hidden";
}

export function formatFeatureList(features: string[], limit: number): string {
  const visible = features.slice(0, limit);
  const remaining = features.length - visible.length;
  return remaining > 0
    ? `${visible.join(", ")} +${remaining}`
    : visible.join(", ");
}

export function formatDateRange(
  startDate: string | null,
  endDate: string | null,
): string {
  if (!startDate || !endDate) return "No usable daily dates";
  const options: Intl.DateTimeFormatOptions = {
    day: "2-digit",
    month: "short",
    year: "numeric",
  };
  const start = new Date(`${startDate}T00:00:00`).toLocaleDateString(
    "en-GB",
    options,
  );
  const end = new Date(`${endDate}T00:00:00`).toLocaleDateString(
    "en-GB",
    options,
  );
  return `${start} – ${end}`;
}

export function hasTrainingEvidence(
  value: unknown,
): value is Record<string, unknown> {
  if (!value || typeof value !== "object") return false;
  const payload = value as Record<string, unknown>;
  return (
    "reports" in payload && "summary" in payload && "data_status" in payload
  );
}

export function hasPortfolioAnalysis(value: unknown): value is Record<string, unknown> {
  if (!hasTrainingEvidence(value)) return false;
  const payload = value as Record<string, unknown>;
  return (
    "analysis_id" in payload &&
    "portfolio" in payload &&
    "plants" in payload &&
    "opportunities" in payload &&
    "provenance" in payload &&
    "finance_status" in payload
  );
}

export function buildLinePath(
  values: number[],
  width: number,
  height: number,
): string {
  if (values.length < 2) return "";
  const minimum = Math.min(...values);
  const range = Math.max(...values) - minimum || 1;
  return values
    .map((value, index) => {
      const x = Number(((index * width) / (values.length - 1)).toFixed(2));
      const y = Number(
        (height - ((value - minimum) * height) / range).toFixed(2),
      );
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
}

export function trainingProgressMessage(isTraining: boolean): string {
  return isTraining
    ? "Validating data, fitting soft sensors, and evaluating holdouts."
    : "No model run in progress.";
}

export function shouldShowTrainingProgress(
  hasAnalysis: boolean,
  isTraining: boolean,
): boolean {
  return !hasAnalysis && isTraining;
}

export function suggestedTsrTarget(current: number, maximum: number): number {
  return Math.min(current + 3, maximum);
}

type CostedOpportunity = { lever: string; annual_savings_rs: number };

export function valuePoolByLever(
  opportunities: CostedOpportunity[],
): { label: string; value: number }[] {
  const values = new Map<string, number>();
  opportunities.forEach((opportunity) => {
    const value = values.get(opportunity.lever) ?? 0;
    values.set(opportunity.lever, value + opportunity.annual_savings_rs);
  });
  return [...values.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((left, right) => right.value - left.value);
}
