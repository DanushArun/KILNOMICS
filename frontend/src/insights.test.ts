import { describe, expect, it } from "vitest";

import {
  buildLinePath,
  hasTrainingEvidence,
  hasPortfolioAnalysis,
  formatDateRange,
  formatFeatureList,
  formatRupees,
  trainingProgressMessage,
  shouldShowTrainingProgress,
  suggestedTsrTarget,
  valuePoolByLever,
} from "./insights";

describe("formatRupees", () => {
  it("formats an annual saving in Indian notation", () => {
    expect(formatRupees(20_904_000)).toBe("₹2.09 Cr");
  });
});

describe("formatFeatureList", () => {
  it("lists model inputs without hiding the remaining count", () => {
    expect(formatFeatureList(["LSF", "SM", "AM", "TSR_pct"], 3)).toBe(
      "LSF, SM, AM +1",
    );
  });
});

describe("formatDateRange", () => {
  it("shows a readable workbook data period", () => {
    expect(formatDateRange("2026-01-01", "2026-02-14")).toBe(
      "01 Jan 2026 – 14 Feb 2026",
    );
  });
});

describe("hasTrainingEvidence", () => {
  it("rejects a response from an out-of-date API server", () => {
    expect(
      hasTrainingEvidence({ reports: {}, source: "demo.xlsx", summary: {} }),
    ).toBe(false);
  });
});

describe("hasPortfolioAnalysis", () => {
  it("rejects a response without the portfolio evidence required by the dashboard", () => {
    expect(
      hasPortfolioAnalysis({ reports: {}, source: "demo.xlsx", summary: {}, data_status: {} }),
    ).toBe(false);
  });
});

describe("buildLinePath", () => {
  it("maps a two-point metric series to the chart bounds", () => {
    expect(buildLinePath([100, 110], 100, 50)).toBe("M 0 50 L 100 0");
  });
});

describe("trainingProgressMessage", () => {
  it("states the actual in-flight training work without inventing a percentage", () => {
    expect(trainingProgressMessage(true)).toContain("Validating data");
  });
});

describe("shouldShowTrainingProgress", () => {
  it("shows progress while a workbook analysis is running without a result", () => {
    expect(shouldShowTrainingProgress(false, true)).toBe(true);
  });
});

describe("suggestedTsrTarget", () => {
  it("starts a scenario above the current TSR without exceeding capability", () => {
    expect(suggestedTsrTarget(10, 16)).toBe(13);
  });
});

describe("valuePoolByLever", () => {
  it("groups the costed opportunity register into a ranked value pool", () => {
    expect(valuePoolByLever([
      { lever: "Fuel mix", annual_savings_rs: 4_000_000 },
      { lever: "Fuel mix", annual_savings_rs: 2_000_000 },
      { lever: "SCM", annual_savings_rs: 5_000_000 },
    ])).toEqual([
      { label: "Fuel mix", value: 6_000_000 },
      { label: "SCM", value: 5_000_000 },
    ]);
  });
});
