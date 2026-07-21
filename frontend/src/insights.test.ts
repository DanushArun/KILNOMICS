import { describe, expect, it } from "vitest";

import { formatRupees } from "./insights";

describe("formatRupees", () => {
  it("formats an annual saving in Indian notation", () => {
    expect(formatRupees(20_904_000)).toBe("₹2.09 Cr");
  });
});
