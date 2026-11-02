// Mock data layer. Shapes mirror future FastAPI responses so each export
// can later be swapped for a fetch call without touching UI components.

export type Status = "normal" | "warning" | "threat" | "offline";
export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type ThreatType =
  | "False Data Injection"
  | "Denial of Service"
  | "Unauthorized Access"
  | "Unknown Anomaly";
export type DetectionMethod = "Rule Engine" | "Isolation Forest" | "Random Forest" | "Hybrid Detection";

export const commandMetrics = {
  gridHealth: 96,
  connectedDevices: 24,
  activeThreats: 0,
  riskScore: 12,
};

export const gridPerformance = Array.from({ length: 24 }, (_, i) => {
  const h = String(i).padStart(2, "0");
  return {
    time: `${h}:00`,
    voltage: +(230 + Math.sin(i / 3) * 2.4 + ((i * 7) % 5) * 0.2).toFixed(1),
    frequency: +(50 + Math.sin(i / 2) * 0.04).toFixed(2),
    load: Math.round(140 + Math.sin((i - 6) / 3.8) * 45 + ((i * 13) % 7)),
  };
});

export const securityOverview = { normal: 1248, suspicious: 3, critical: 0 };

export const recentEvents = [
  { id: 1, text: "Smart Meter SM-04 telemetry verified", time: "13:34:12" },
  { id: 2, text: "Substation network connection stable", time: "13:32:48" },
  { id: 3, text: "Security monitoring cycle completed", time: "13:30:00" },
  { id: 4, text: "Feeder A data integrity verified", time: "13:27:31" },
  { id: 5, text: "No critical anomalies detected", time: "13:25:05" },
];

export const gridStatus = ["Main Substation", "Feeder A", "Feeder B", "Smart Meter Cluster"];

export type GridNode = {
  id: string;
  label: string;
  type: "Power Source" | "Substation" | "Feeder" | "Smart Meter";
  voltage: string;
  current: string;
  frequency: string;
  power: string;
  latency: number;
  risk: number;
};

export const topologyNodes: GridNode[] = [
  { id: "PS-01", label: "Power Source", type: "Power Source", voltage: "132 kV", current: "1,210 A", frequency: "50.00 Hz", power: "160 MW", latency: 6, risk: 4 },
  { id: "SUB-01", label: "Main Substation", type: "Substation", voltage: "33 kV", current: "2,840 A", frequency: "50.01 Hz", power: "158 MW", latency: 9, risk: 8 },
  { id: "FDR-A", label: "Feeder A", type: "Feeder", voltage: "11 kV", current: "4,120 A", frequency: "50.00 Hz", power: "78 MW", latency: 12, risk: 10 },
  { id: "FDR-B", label: "Feeder B", type: "Feeder", voltage: "11 kV", current: "4,050 A", frequency: "49.99 Hz", power: "77 MW", latency: 13, risk: 9 },
  ...["01", "02", "03", "04", "05", "06"].map((n, i) => ({
    id: `SM-${n}`,
    label: `Smart Meter ${n}`,
    type: "Smart Meter" as const,
    voltage: `${(230 + i * 0.4).toFixed(1)} V`,
    current: `${(18 + i * 1.3).toFixed(1)} A`,
    frequency: "50.00 Hz",
    power: `${(4.1 + i * 0.3).toFixed(1)} kW`,
    latency: 18 + i * 2,
    risk: 6 + i,
  })),
];

export const threatSummary = { total: 1251, detected: 3, high: 1, critical: 0 };

export type Alert = {
  id: string;
  time: string;
  device: string;
  type: ThreatType;
  method: DetectionMethod;
  confidence: number;
  severity: Severity;
  status: "Open" | "Investigating" | "Contained" | "Resolved";
  risk: number;
  summary: string;
  evidence: string[];
  response: string[];
};

export const alerts: Alert[] = [
  {
    id: "ALT-2041", time: "13:21:44", device: "SM-04", type: "False Data Injection", method: "Hybrid Detection",
    confidence: 91, severity: "HIGH", status: "Investigating", risk: 78,
    summary: "Reported consumption from SM-04 diverges from feeder-level measurements, consistent with manipulated telemetry.",
    evidence: ["Voltage reading deviates 8.2% from Feeder A baseline", "Power balance mismatch of 3.4 kW across feeder", "Reading pattern outside 99th percentile (Isolation Forest)", "Timestamp sequence irregularity detected"],
    response: ["Flag suspicious data", "Isolate affected device", "Switch to trusted telemetry"],
  },
  {
    id: "ALT-2038", time: "12:58:10", device: "FDR-B", type: "Denial of Service", method: "Rule Engine",
    confidence: 76, severity: "MEDIUM", status: "Contained", risk: 54,
    summary: "Burst of malformed polling requests targeted the Feeder B gateway, raising communication latency.",
    evidence: ["Request rate 6.1× above normal", "Network latency rose from 13 ms to 64 ms", "Repeated requests from a single source address"],
    response: ["Limit suspicious traffic", "Prioritize critical communication", "Generate security alert"],
  },
  {
    id: "ALT-2033", time: "11:42:37", device: "SM-02", type: "Unknown Anomaly", method: "Isolation Forest",
    confidence: 62, severity: "LOW", status: "Resolved", risk: 22,
    summary: "Short-lived irregular reporting interval on SM-02; no evidence of malicious intent after review.",
    evidence: ["Reporting interval varied by ±40 s", "Anomaly score 0.61 (threshold 0.58)", "No correlated events on neighbouring meters"],
    response: ["Monitor device for recurrence", "Verify firmware integrity", "Close after observation window"],
  },
];

export type AttackKey = "normal" | "fdi" | "dos" | "ua";

export const attackScenarios: Record<AttackKey, {
  title: string;
  description: string;
  stage: number;
  gridHealth: number;
  latency: number;
  confidence: number;
  risk: number;
  target?: string;
}> = {
  normal: { title: "Normal Operation", description: "Return the simulated grid to a stable state.", stage: 0, gridHealth: 96, latency: 12, confidence: 0, risk: 12 },
  fdi: { title: "False Data Injection", description: "Manipulates reported electrical telemetry data.", stage: 5, gridHealth: 72, latency: 48, confidence: 94, risk: 92, target: "SM-04" },
  dos: { title: "Denial of Service", description: "Simulates communication overload and increased network latency.", stage: 4, gridHealth: 81, latency: 286, confidence: 88, risk: 74, target: "FDR-B" },
  ua: { title: "Unauthorized Access", description: "Simulates suspicious access to a smart-grid device.", stage: 3, gridHealth: 89, latency: 21, confidence: 83, risk: 81, target: "SUB-01" },
};

export const simulationStages = [
  "Normal Operation", "Attack Initiated", "Anomaly Detected", "AI Analysis", "Threat Classified", "Response Initiated",
];

export type Incident = {
  id: string;
  type: Exclude<ThreatType, "Unknown Anomaly">;
  device: string;
  severity: Severity;
  time: string;
  risk: number;
  status: "Open" | "Investigating" | "Contained" | "Resolved";
};

export const incidents: Incident[] = [
  { id: "INC-0117", type: "False Data Injection", device: "SM-04", severity: "HIGH", time: "2026-11-02 13:21", risk: 78, status: "Investigating" },
  { id: "INC-0116", type: "Unauthorized Access", device: "SUB-01", severity: "HIGH", time: "2026-11-02 12:05", risk: 71, status: "Open" },
  { id: "INC-0115", type: "Denial of Service", device: "FDR-B", severity: "MEDIUM", time: "2026-11-02 10:48", risk: 54, status: "Contained" },
  { id: "INC-0114", type: "False Data Injection", device: "SM-06", severity: "MEDIUM", time: "2026-11-01 22:16", risk: 46, status: "Resolved" },
  { id: "INC-0113", type: "Denial of Service", device: "FDR-A", severity: "LOW", time: "2026-11-01 17:39", risk: 28, status: "Resolved" },
];

export const incidentResponses: Record<Incident["type"], string[]> = {
  "False Data Injection": ["Flag suspicious data", "Isolate affected device", "Switch to trusted telemetry"],
  "Denial of Service": ["Limit suspicious traffic", "Prioritize critical communication", "Generate security alert"],
  "Unauthorized Access": ["Terminate suspicious session", "Lock affected access", "Escalate the incident"],
};

export const incidentStages = ["Detected", "Analyzed", "Contained", "Resolved"];
