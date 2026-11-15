import { describe, expect, it } from "vitest";
import { simulateTelemetry } from "@/lib/simulation-model";
import { simulationTargets } from "@/data/mock";
const time = "2026-11-15T09:00:00.000Z";
describe("simulated telemetry and detection", () => {
  it("starts normally with approximately 230 V, 50 Hz and no failed logins", () => {
    const normal = simulateTelemetry({ deviceId: "SM-01", attack: "normal" }, 0, time);
    expect(normal.telemetry.voltage).toBe("230.0 V"); expect(normal.telemetry.frequency).toBe("50.00 Hz");
    expect(normal.telemetry.failedLogins).toBe(0); expect(normal.telemetry.packetLoss).toBe(0.1);
    expect(normal.detection).toBeNull(); expect(normal.incident).toBeNull();
  });
  it("FDI changes electrical telemetry and produces the requested 72/48/94/92 metrics", () => {
    const result = simulateTelemetry({ deviceId: "SM-04", attack: "fdi" }, 1, time);
    expect(result.gridHealth).toBe(72); expect(result.telemetry.latency).toBe(48);
    expect(result.detection?.confidence).toBe(94); expect(result.detection?.risk).toBe(92);
    expect(result.telemetry.voltage).toBe("272.8 V"); expect(result.telemetry.power).toBe("8.3 kW");
    expect(result.detection?.anomalyScore).toBe(0.91); expect(result.detection?.classificationConfidence).toBe(94);
  });
  it("DoS increases latency, packet rate and packet loss", () => {
    const result = simulateTelemetry({ deviceId: "FDR-B", attack: "dos" }, 2, time);
    expect(result.telemetry.latency).toBe(286); expect(result.telemetry.packetRate).toBe(4200); expect(result.telemetry.packetLoss).toBe(18.6);
  });
  it("unauthorized access creates multiple failed login attempts", () => {
    const result = simulateTelemetry({ deviceId: "SM-02", attack: "ua" }, 3, time);
    expect(result.telemetry.failedLogins).toBe(17); expect(result.telemetry.packetRate).toBe(380);
  });
  it("all eight selected devices carry through detection and incident creation", () => {
    expect(simulationTargets).toEqual(["SM-01", "SM-02", "SM-03", "SM-04", "SM-05", "SM-06", "FDR-A", "FDR-B"]);
    for (const deviceId of simulationTargets) {
      const result = simulateTelemetry({ deviceId, attack: "fdi" }, 4, time);
      expect(result.detection?.device).toBe(deviceId); expect(result.incident?.device).toBe(deviceId);
      expect(result.incident?.status).toBe("Open"); expect(result.incident?.severity).toBe("CRITICAL");
    }
  });
  it("reset restores normal target telemetry", () => {
    const active = simulateTelemetry({ deviceId: "SM-04", attack: "ua" }, 5, time);
    const reset = simulateTelemetry({ ...active.request, attack: "normal" }, 5, time);
    expect(reset.telemetry.failedLogins).toBe(0); expect(reset.gridHealth).toBe(96); expect(reset.detection).toBeNull();
  });
});
