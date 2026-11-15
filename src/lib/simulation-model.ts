import {
  attackScenarios, incidentResponses, simulationAnalysis, simulationTelemetryChanges, simulationTargets, topologyNodes,
  type Alert, type SimulationRequest, type SimulationResult, type Telemetry,
} from "@/data/mock";
import { getRiskSeverity } from "@/lib/risk";

function scaleMeasurement(value: string, factor: number): string {
  const [number, unit] = value.split(" ");
  return `${(Number(number?.replaceAll(",", "")) * factor).toFixed(1)} ${unit ?? ""}`;
}

// Pure mock adapter: a future FastAPI response can return this same result shape.
export function simulateTelemetry(request: SimulationRequest, runId: number, timestamp: string): SimulationResult {
  const node = topologyNodes.find((item) => item.id === request.deviceId);
  if (!node || !simulationTargets.includes(request.deviceId)) throw new Error("Select a valid target device");
  const scenario = attackScenarios[request.attack];
  const telemetry: Telemetry = {
    voltage: node.voltage, current: node.current, frequency: node.frequency, power: node.power,
    latency: node.latency, packetRate: node.packetRate, packetLoss: node.packetLoss, failedLogins: node.failedLogins,
    ...simulationTelemetryChanges[request.attack],
  };
  if (request.attack === "normal") return { request, telemetry, gridHealth: scenario.gridHealth, detection: null, incident: null };
  if (request.attack === "fdi") {
    telemetry.voltage = scaleMeasurement(node.voltage, 1.18);
    telemetry.current = scaleMeasurement(node.current, 1.32);
    telemetry.frequency = "50.62 Hz";
    telemetry.power = scaleMeasurement(node.power, 1.65);
  }
  const analysis = simulationAnalysis[request.attack];
  const type = request.attack === "fdi" ? "False Data Injection" : request.attack === "dos" ? "Denial of Service" : "Unauthorized Access";
  const detection: Alert = {
    id: `ALT-SIM-${String(runId).padStart(4, "0")}`, time: timestamp.slice(11, 19), device: node.id, type,
    method: "Hybrid Detection", confidence: scenario.confidence, severity: getRiskSeverity(scenario.risk),
    status: "Open", risk: scenario.risk, summary: `${type} detected in simulated telemetry from ${node.id}.`,
    evidence: [...analysis.triggeredRules, `Isolation Forest anomaly score: ${analysis.anomalyScore}`],
    response: incidentResponses[type], ...analysis,
  };
  return {
    request, telemetry, gridHealth: scenario.gridHealth, detection,
    incident: { id: `INC-SIM-${String(runId).padStart(4, "0")}`, device: node.id, type, severity: detection.severity, time: timestamp.slice(0, 16).replace("T", " "), risk: scenario.risk, status: "Open" },
  };
}