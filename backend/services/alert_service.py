from datetime import datetime
from typing import List, Optional, Dict
from ..models.schemas import AlertSchema, ThreatType, DetectionMethod, SeverityLevel, IncidentStatus

class AlertService:
    """
    In-memory Alert Management Service.
    Stores and manages alerts produced by the hybrid threat detection pipeline.
    """

    def __init__(self):
        self._alerts: List[AlertSchema] = [
            AlertSchema(
                id="ALT-2041",
                time="13:21:44",
                device="SM-04",
                type="False Data Injection",
                method="Hybrid Detection",
                confidence=91,
                severity="HIGH",
                status="Investigating",
                risk=78,
                summary="Reported consumption from SM-04 diverges from feeder-level measurements, consistent with manipulated telemetry.",
                evidence=[
                    "Voltage reading deviates 8.2% from Feeder A baseline",
                    "Power balance mismatch of 3.4 kW across feeder",
                    "Reading pattern outside 99th percentile (Isolation Forest)",
                    "Timestamp sequence irregularity detected",
                ],
                response=["Flag suspicious data", "Isolate affected device", "Switch to trusted telemetry"],
            ),
            AlertSchema(
                id="ALT-2038",
                time="12:58:10",
                device="FDR-B",
                type="Denial of Service",
                method="Rule Engine",
                confidence=76,
                severity="MEDIUM",
                status="Contained",
                risk=54,
                summary="Burst of malformed polling requests targeted the Feeder B gateway, raising communication latency.",
                evidence=[
                    "Request rate 6.1× above normal",
                    "Network latency rose from 13 ms to 64 ms",
                    "Repeated requests from a single source address",
                ],
                response=["Limit suspicious traffic", "Prioritize critical communication", "Generate security alert"],
            ),
            AlertSchema(
                id="ALT-2033",
                time="11:42:37",
                device="SM-02",
                type="Unknown Anomaly",
                method="Isolation Forest",
                confidence=62,
                severity="LOW",
                status="Resolved",
                risk=22,
                summary="Short-lived irregular reporting interval on SM-02; no evidence of malicious intent after review.",
                evidence=[
                    "Reporting interval varied by ±40 s",
                    "Anomaly score 0.61 (threshold 0.58)",
                    "No correlated events on neighbouring meters",
                ],
                response=["Monitor device for recurrence", "Verify firmware integrity", "Close after observation window"],
            ),
        ]
        self._next_alert_num = 2042

    def get_all(self, limit: int = 50) -> List[AlertSchema]:
        """Return alerts ordered newest first."""
        return self._alerts[:limit]

    def get_by_id(self, alert_id: str) -> Optional[AlertSchema]:
        for a in self._alerts:
            if a.id == alert_id:
                return a
        return None

    def create_alert(
        self,
        device: str,
        threat_type: ThreatType,
        method: DetectionMethod,
        confidence: int,
        severity: SeverityLevel,
        risk: int,
        summary: str,
        evidence: List[str],
        response: List[str],
        status: IncidentStatus = "Open",
    ) -> AlertSchema:
        alert_id = f"ALT-{self._next_alert_num}"
        self._next_alert_num += 1
        now_time = datetime.now().strftime("%H:%M:%S")

        alert = AlertSchema(
            id=alert_id,
            time=now_time,
            device=device,
            type=threat_type,
            method=method,
            confidence=confidence,
            severity=severity,
            status=status,
            risk=risk,
            summary=summary,
            evidence=evidence,
            response=response,
        )
        # Prepend to front so newest alerts appear first
        self._alerts.insert(0, alert)
        return alert

    def reset_to_initial(self):
        """Restore initial state."""
        self.__init__()
