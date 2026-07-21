import { describe, expect, it } from "vitest";

import { formatFeatureList, formatRupees } from "./insights";

describe("formatRupees", () => {
  it("formats an annual saving in Indian notation", () => {
    expect(formatRupees(20_904_000)).toBe("₹2.09 Cr");
  });
});

describe("formatFeatureList", () => {
  it("lists model inputs without hiding the remaining count", () => {
    expect(formatFeatureList(["LSF", "SM", "AM", "TSR_pct"], 3)).toBe("LSF, SM, AM +1");
  });
});
