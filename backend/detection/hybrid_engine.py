from typing import Dict, List, Optional
from ..models.schemas import DeviceTelemetry, DetectionResult, DetectionMethod, ThreatType
from .rule_engine import RuleBasedDetectionEngine
from .anomaly_detector import IsolationForestAnomalyDetector
from .attack_classifier import RandomForestAttackClassifier

class HybridThreatDecisionEngine:
    """
    Multi-layered Hybrid Threat Decision Engine:
    Correlates Rule Engine, Isolation Forest, and Random Forest Classifier outputs
    to produce an explainable, robust cybersecurity decision.
    """

    def __init__(
        self,
        rule_engine: RuleBasedDetectionEngine,
        anomaly_detector: IsolationForestAnomalyDetector,
        classifier: RandomForestAttackClassifier,
    ):
        self.rule_engine = rule_engine
        self.anomaly_detector = anomaly_detector
        self.classifier = classifier

    def evaluate(self, telem: DeviceTelemetry, nominals: Dict[str, float]) -> DetectionResult:
        nom_v = nominals.get("nominal_v", 230.0)

        # 1. Rule Engine Evaluation
        rule_res = self.rule_engine.evaluate(telem, nominal_voltage=nom_v)
        rule_suspicious: bool = rule_res["suspicious"]
        triggered_rules: List[str] = rule_res["triggered_rules"]
        rule_evidence: List[str] = rule_res["evidence"]

        # 2. Isolation Forest Anomaly Detection
        is_anomaly, anomaly_score = self.anomaly_detector.predict(telem, nominals)

        # 3. Random Forest Attack Classification
        pred_class, rf_conf, class_probs = self.classifier.predict(telem, nominals)

        # 4. Hybrid Fusion Logic
        detection_methods: List[DetectionMethod] = []
        evidence: List[str] = list(rule_evidence)
        final_threat_type: ThreatType = "Normal"
        final_confidence: float = 0.0
        suspicious: bool = False
        summary = ""

        if is_anomaly:
            evidence.append(f"Reading pattern outside 99th percentile (Isolation Forest score: {anomaly_score:.2f})")

        # Fusion Decision Matrix
        if pred_class == "False Data Injection" and (rule_suspicious or is_anomaly):
            final_threat_type = "False Data Injection"
            suspicious = True
            detection_methods = ["Rule Engine", "Isolation Forest", "Random Forest", "Hybrid Detection"]
            final_confidence = max(88.0, min(96.0, rf_conf * 0.6 + (anomaly_score * 100) * 0.4))
            summary = (
                f"Reported consumption and electrical measurements from {telem.device_name} ({telem.device_id}) "
                f"diverge significantly from feeder baseline, indicating manipulated telemetry."
            )

        elif pred_class == "Denial of Service" and (rule_suspicious or is_anomaly):
            final_threat_type = "Denial of Service"
            suspicious = True
            detection_methods = ["Rule Engine", "Isolation Forest", "Random Forest", "Hybrid Detection"]
            final_confidence = max(82.0, min(95.0, rf_conf * 0.7 + (anomaly_score * 100) * 0.3))
            summary = (
                f"Volumetric flood and extreme latency detected on communication interface of {telem.device_name} ({telem.device_id}), "
                f"causing communication degradation."
            )

        elif pred_class == "Unauthorized Access" and (rule_suspicious or telem.failed_login_attempts > 0):
            final_threat_type = "Unauthorized Access"
            suspicious = True
            detection_methods = ["Rule Engine", "Random Forest", "Hybrid Detection"]
            final_confidence = max(80.0, min(94.0, rf_conf * 0.8 + min(20.0, telem.failed_login_attempts * 1.5)))
            summary = (
                f"Multiple failed authentication attempts and brute-force indicators detected on {telem.device_name} ({telem.device_id}) "
                f"management interface."
            )

        elif is_anomaly and not rule_suspicious and pred_class == "Normal":
            # Anomaly detected by unsupervised IF, but unclassified by supervised rules
            final_threat_type = "Unknown Anomaly"
            suspicious = True
            detection_methods = ["Isolation Forest"]
            final_confidence = round(anomaly_score * 100.0, 1)
            summary = (
                f"Short-lived behavioral variation detected on {telem.device_name} ({telem.device_id}); "
                f"flagged by Isolation Forest for monitoring."
            )

        else:
            final_threat_type = "Normal"
            suspicious = False
            detection_methods = ["Rule Engine", "Isolation Forest", "Random Forest"]
            final_confidence = 0.0
            summary = f"All security monitoring controls active. Telemetry for {telem.device_name} ({telem.device_id}) is normal."

        return DetectionResult(
            suspicious=suspicious,
            final_threat_type=final_threat_type,
            final_confidence=round(final_confidence, 1),
            detection_methods_used=detection_methods,
            anomaly_detected=is_anomaly,
            anomaly_score=anomaly_score,
            triggered_rules=triggered_rules,
            evidence=evidence,
            class_probabilities=class_probs,
            summary=summary,
        )
