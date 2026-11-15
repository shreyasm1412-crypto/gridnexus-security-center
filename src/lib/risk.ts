import type { Severity, Status } from "@/data/mock";

export type RiskTone = Status | "high";

export function getRiskSeverity(score: number): Severity {
  if (score <= 25) return "LOW";
  if (score <= 50) return "MEDIUM";
  if (score <= 75) return "HIGH";
  return "CRITICAL";
}

export function riskTone(score: number): RiskTone {
  const tones: Record<Severity, RiskTone> = { LOW: "normal", MEDIUM: "warning", HIGH: "high", CRITICAL: "threat" };
  return tones[getRiskSeverity(score)];
}