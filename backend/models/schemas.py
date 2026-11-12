from __future__ import annotations
from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

DeviceStatus = Literal["normal", "warning", "threat", "offline"]
SeverityLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
ThreatType = Literal[
    "Normal",
    "False Data Injection",
    "Denial of Service",
    "Unauthorized Access",
    "Unknown Anomaly",
]
DetectionMethod = Literal[
    "Rule Engine",
    "Isolation Forest",
    "Random Forest",
    "Hybrid Detection",
]
IncidentStatus = Literal["Open", "Investigating", "Contained", "Resolved"]
AttackKey = Literal["normal", "fdi", "dos", "ua"]

class DeviceTelemetry(BaseModel):
    device_id: str
    device_name: str
    device_type: Literal["Power Source", "Substation", "Feeder", "Smart Meter"]
    status: DeviceStatus = "normal"
    voltage: float
    current: float
    frequency: float
    power: float
    network_latency: float
    packet_rate: float
    packet_loss: float
    failed_login_attempts: int = 0
    timestamp: str

class GridNodeSchema(BaseModel):
    id: str
    label: str
    type: Literal["Power Source", "Substation", "Feeder", "Smart Meter"]
    voltage: str
    current: str
    frequency: str
    power: str
    latency: int
    risk: int
    status: DeviceStatus = "normal"
    telemetry: Optional[DeviceTelemetry] = None

class DetectionResult(BaseModel):
    suspicious: bool
    final_threat_type: ThreatType
    final_confidence: float
    detection_methods_used: List[DetectionMethod]
    anomaly_detected: bool
    anomaly_score: float = 0.0
    triggered_rules: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    class_probabilities: Dict[str, float] = Field(default_factory=dict)
    summary: str = ""

class RiskResult(BaseModel):
    risk_score: int
    severity: SeverityLevel
    risk_factors: List[str] = Field(default_factory=list)

class AlertSchema(BaseModel):
    id: str
    time: str
    device: str
    type: ThreatType
    method: DetectionMethod
    confidence: int
    severity: SeverityLevel
    status: IncidentStatus = "Open"
    risk: int
    summary: str
    evidence: List[str] = Field(default_factory=list)
    response: List[str] = Field(default_factory=list)

class IncidentTimelineEvent(BaseModel):
    stage: str
    time: str
    completed: bool

class IncidentSchema(BaseModel):
    id: str
    type: Literal["False Data Injection", "Denial of Service", "Unauthorized Access"]
    device: str
    severity: SeverityLevel
    time: str
    risk: int
    status: IncidentStatus = "Open"
    timeline: List[IncidentTimelineEvent] = Field(default_factory=list)
    recommended_response: List[str] = Field(default_factory=list)

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus

class SimulationResponse(BaseModel):
    mode: AttackKey
    title: str
    description: str
    target: Optional[str] = None
    stage: int
    grid_health: int
    latency: int
    confidence: int
    risk: int
    detection: Optional[DetectionResult] = None
    risk_assessment: Optional[RiskResult] = None
    active_alert: Optional[AlertSchema] = None
    active_incident: Optional[IncidentSchema] = None
    message: str

class GridPerformancePoint(BaseModel):
    time: str
    voltage: float
    frequency: float
    load: float

class SecurityOverview(BaseModel):
    normal: int
    suspicious: int
    critical: int

class RecentEvent(BaseModel):
    id: int
    text: str
    time: str

class SystemStatusItem(BaseModel):
    label: str
    value: str
    status: DeviceStatus

class DashboardResponse(BaseModel):
    grid_health: int
    security_status: str
    connected_devices: int
    active_threats: int
    overall_risk: int
    system_status: List[SystemStatusItem]
    security_overview: SecurityOverview
    recent_events: List[RecentEvent]
    grid_status: List[str]
    grid_performance: List[GridPerformancePoint]
    active_attack: AttackKey
    active_target: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str
    models_loaded: bool = True
