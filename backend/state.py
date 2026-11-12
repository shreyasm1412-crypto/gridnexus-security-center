import os
from .simulator.grid_simulator import SmartGridDigitalTwin
from .simulator.attack_simulator import AttackSimulator
from .detection.rule_engine import RuleBasedDetectionEngine
from .detection.anomaly_detector import IsolationForestAnomalyDetector
from .detection.attack_classifier import RandomForestAttackClassifier
from .detection.hybrid_engine import HybridThreatDecisionEngine
from .services.risk_engine import RiskAndSeverityEngine
from .services.alert_service import AlertService
from .services.incident_service import IncidentService

# Paths for saved models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "data", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

IF_MODEL_PATH = os.path.join(MODELS_DIR, "isolation_forest.joblib")
RF_MODEL_PATH = os.path.join(MODELS_DIR, "attack_classifier.joblib")

# Core singletons
twin = SmartGridDigitalTwin()
attack_simulator = AttackSimulator(twin)

rule_engine = RuleBasedDetectionEngine()
anomaly_detector = IsolationForestAnomalyDetector(model_path=IF_MODEL_PATH)
attack_classifier = RandomForestAttackClassifier(model_path=RF_MODEL_PATH)

hybrid_engine = HybridThreatDecisionEngine(
    rule_engine=rule_engine,
    anomaly_detector=anomaly_detector,
    classifier=attack_classifier,
)

risk_engine = RiskAndSeverityEngine()
alert_service = AlertService()
incident_service = IncidentService()
