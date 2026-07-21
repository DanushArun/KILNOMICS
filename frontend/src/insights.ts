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
  return remaining > 0 ? `${visible.join(", ")} +${remaining}` : visible.join(", ");
}
