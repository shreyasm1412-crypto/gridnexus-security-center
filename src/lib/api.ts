import {
  alerts as fallbackAlerts,
  commandMetrics as fallbackMetrics,
  gridPerformance as fallbackPerformance,
  gridStatus as fallbackGridStatus,
  incidents as fallbackIncidents,
  recentEvents as fallbackEvents,
  securityOverview as fallbackOverview,
  systemStatus as fallbackSystemStatus,
  topologyNodes as fallbackNodes,
  type Alert,
  type AttackKey,
  type GridNode,
  type Incident,
  type Status,
} from "@/data/mock";

// Base API URL: uses relative /api (proxied by Vite) or direct backend port 8000
const API_BASE = typeof window !== "undefined" && (window.location.port === "8080" || window.location.port === "5173")
  ? "/api"
  : "http://localhost:8000/api";

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T | null> {
  // 1. Direct call to FastAPI backend on port 8000 (CORS enabled)
  try {
    const directRes = await fetch(`http://localhost:8000/api${endpoint}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (directRes.ok) return await directRes.json();
  } catch {
    // Backend direct connection failed, try proxy next
  }

  // 2. Relative /api call (Vite dev proxy)
  try {
    const res = await fetch(`/api${endpoint}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (res.ok) return await res.json();
  } catch {
    // Both failed
  }

  return null;
}

// ---------------------------------------------------------------------------
// 1. Dashboard
// ---------------------------------------------------------------------------
export type DashboardData = {
  gridHealth: number;
  securityStatus: string;
  connectedDevices: number;
  activeThreats: number;
  overallRisk: number;
  securityOverview: { normal: number; suspicious: number; critical: number };
  recentEvents: Array<{ id: number; text: string; time: string }>;
  gridStatus: string[];
  gridPerformance: Array<{ time: string; voltage: number; frequency: number; load: number }>;
  activeAttack: AttackKey;
  activeTarget: string | null;
};

export async function fetchDashboard(): Promise<DashboardData> {
  const data = await apiFetch<any>("/dashboard");
  if (!data) {
    return {
      gridHealth: fallbackMetrics.gridHealth,
      securityStatus: "Secure",
      connectedDevices: fallbackMetrics.connectedDevices,
      activeThreats: fallbackMetrics.activeThreats,
      overallRisk: fallbackMetrics.riskScore,
      securityOverview: fallbackOverview,
      recentEvents: fallbackEvents,
      gridStatus: fallbackGridStatus,
      gridPerformance: fallbackPerformance,
      activeAttack: "normal",
      activeTarget: null,
    };
  }

  return {
    gridHealth: data.grid_health ?? fallbackMetrics.gridHealth,
    securityStatus: data.security_status ?? "Secure",
    connectedDevices: data.connected_devices ?? 24,
    activeThreats: data.active_threats ?? 0,
    overallRisk: data.overall_risk ?? 12,
    securityOverview: data.security_overview ?? fallbackOverview,
    recentEvents: data.recent_events ?? fallbackEvents,
    gridStatus: data.grid_status ?? fallbackGridStatus,
    gridPerformance: data.grid_performance ?? fallbackPerformance,
    activeAttack: data.active_attack ?? "normal",
    activeTarget: data.active_target ?? null,
  };
}

// ---------------------------------------------------------------------------
// 2. Topology & Devices
// ---------------------------------------------------------------------------
export async function fetchTopology(): Promise<{ nodes: GridNode[]; attackMode: AttackKey; target?: string }> {
  const data = await apiFetch<any>("/grid/topology");
  if (!data || !data.nodes) {
    return { nodes: fallbackNodes, attackMode: "normal" };
  }

  const nodes: GridNode[] = data.nodes.map((n: any) => ({
    id: n.id,
    label: n.label,
    type: n.type,
    voltage: n.voltage,
    current: n.current,
    frequency: n.frequency,
    power: n.power,
    latency: n.latency,
    risk: n.risk,
  }));

  return {
    nodes,
    attackMode: data.attack_mode ?? "normal",
    target: data.attack_target,
  };
}

// ---------------------------------------------------------------------------
// 3. Alerts
// ---------------------------------------------------------------------------
export async function fetchAlerts(): Promise<Alert[]> {
  const data = await apiFetch<Alert[]>("/alerts");
  if (!data || !Array.isArray(data)) {
    return fallbackAlerts;
  }
  return data;
}

// ---------------------------------------------------------------------------
// 4. Incidents
// ---------------------------------------------------------------------------
export async function fetchIncidents(): Promise<Incident[]> {
  const data = await apiFetch<Incident[]>("/incidents");
  if (!data || !Array.isArray(data)) {
    return fallbackIncidents;
  }
  return data;
}

export async function updateIncidentStatus(id: string, status: Incident["status"]): Promise<Incident | null> {
  const data = await apiFetch<Incident>(`/incidents/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
  return data;
}

// ---------------------------------------------------------------------------
// 5. Attack Simulation Triggers
// ---------------------------------------------------------------------------
export async function triggerSimulation(mode: AttackKey): Promise<any> {
  const endpoint =
    mode === "normal"
      ? "/simulation/normal"
      : mode === "fdi"
      ? "/simulation/fdi"
      : mode === "dos"
      ? "/simulation/dos"
      : "/simulation/unauthorized-access";

  const data = await apiFetch<any>(endpoint, { method: "POST" });
  return data;
}
