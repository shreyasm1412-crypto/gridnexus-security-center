import { describe, expect, it } from "vitest";
import { getRiskSeverity, riskTone } from "@/lib/risk";
import { alerts, incidents } from "@/data/mock";

describe("shared risk system", () => {
  it("scores 0–25 are LOW and green", () => { for (let score = 0; score <= 25; score++) { expect(getRiskSeverity(score)).toBe("LOW"); expect(riskTone(score)).toBe("normal"); } });
  it("scores 26–50 are MEDIUM and yellow", () => { for (let score = 26; score <= 50; score++) { expect(getRiskSeverity(score)).toBe("MEDIUM"); expect(riskTone(score)).toBe("warning"); } });
  it("scores 51–75 are HIGH and orange", () => { for (let score = 51; score <= 75; score++) { expect(getRiskSeverity(score)).toBe("HIGH"); expect(riskTone(score)).toBe("high"); } });
  it("scores 76–100 are CRITICAL and red", () => { for (let score = 76; score <= 100; score++) { expect(getRiskSeverity(score)).toBe("CRITICAL"); expect(riskTone(score)).toBe("threat"); } });
  it("mock alert and incident severities follow their scores", () => { for (const record of [...alerts, ...incidents]) expect(record.severity).toBe(getRiskSeverity(record.risk)); });
});
