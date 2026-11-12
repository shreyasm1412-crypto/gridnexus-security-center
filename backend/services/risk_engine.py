from typing import List, Tuple
from ..models.schemas import DeviceTelemetry, DetectionResult, RiskResult, SeverityLevel

class RiskAndSeverityEngine:
    """
    Deterministic risk calculation combining:
    - AI classifier confidence
    - Anomaly detection score
    - Rule trigger count & severity
    - Device asset criticality weight
    - Electrical and network operational impact
    """

    CRITICALITY_WEIGHTS = {
        "Power Source": 1.4,
        "Substation": 1.3,
        "Feeder": 1.15,
        "Smart Meter": 1.0,
    }

    def calculate_risk(
        self,
        telem: DeviceTelemetry,
        detection: DetectionResult,
        nominal_voltage: float = 230.0,
    ) -> RiskResult:
        if not detection.suspicious or detection.final_threat_type == "Normal":
            return RiskResult(
                risk_score=12,
                severity="LOW",
                risk_factors=["Baseline operational telemetry normal", "No active anomaly triggers"],
            )

        factors: List[str] = []
        base_score = 0.0

        # 1. AI Confidence Factor (weight ~ 30%)
        conf_component = (detection.final_confidence / 100.0) * 30.0
        base_score += conf_component
        factors.append(f"AI Detection Confidence ({detection.final_confidence:.0f}%) contributed +{conf_component:.1f} pts")

        # 2. Anomaly Factor (weight ~ 20%)
        if detection.anomaly_detected:
            anom_component = max(10.0, detection.anomaly_score * 20.0)
            base_score += anom_component
            factors.append(f"Isolation Forest Anomaly (score: {detection.anomaly_score:.2f}) contributed +{anom_component:.1f} pts")

        # 3. Rule Triggers Factor (weight ~ 25%)
        num_rules = len(detection.triggered_rules)
        rule_component = min(25.0, num_rules * 8.0)
        base_score += rule_component
        if num_rules > 0:
            factors.append(f"{num_rules} rule triggers added +{rule_component:.1f} pts")

        # 4. Impact Component (Electrical or Network) (weight ~ 15%)
        impact_score = 0.0
        if detection.final_threat_type == "False Data Injection":
            dev_pct = abs(telem.voltage - nominal_voltage) / nominal_voltage * 100.0 if nominal_voltage > 0 else 0
            impact_score = min(15.0, dev_pct * 0.8)
            factors.append(f"Electrical distortion impact: {dev_pct:.1f}% voltage variance")
        elif detection.final_threat_type == "Denial of Service":
            lat_impact = min(15.0, (telem.network_latency / 250.0) * 15.0)
            impact_score = lat_impact
            factors.append(f"Network degradation impact: {telem.network_latency:.0f} ms latency")
        elif detection.final_threat_type == "Unauthorized Access":
            auth_impact = min(15.0, telem.failed_login_attempts * 1.0)
            impact_score = auth_impact
            factors.append(f"Access breach intensity: {telem.failed_login_attempts} failed attempts")
        base_score += impact_score

        # 5. Asset Criticality Multiplier
        crit_multiplier = self.CRITICALITY_WEIGHTS.get(telem.device_type, 1.0)
        raw_final = base_score * crit_multiplier
        if crit_multiplier > 1.0:
            factors.append(f"Tier-1 Asset Multiplier ({telem.device_type} ×{crit_multiplier:.2f}) applied")

        # Clamp between 0 and 100
        risk_score = int(round(max(0.0, min(100.0, raw_final))))

        # Severity bracket mapping
        severity: SeverityLevel
        if risk_score >= 75:
            severity = "CRITICAL"
        elif risk_score >= 50:
            severity = "HIGH"
        elif risk_score >= 25:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        return RiskResult(
            risk_score=risk_score,
            severity=severity,
            risk_factors=factors,
        )
