import { describe, expect, it } from "vitest";

import {
  buildLinePath,
  hasTrainingEvidence,
  formatDateRange,
  formatFeatureList,
  formatRupees,
  trainingProgressMessage,
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
