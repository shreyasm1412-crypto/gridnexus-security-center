import os
import math
import random
from typing import Dict, Tuple, List, Optional
import numpy as np

# Attempt scikit-learn import
try:
    from sklearn.ensemble import IsolationForest
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    joblib = None

from ..models.schemas import DeviceTelemetry

class IsolationForestAnomalyDetector:
    """
    Genuine scikit-learn Isolation Forest anomaly detector for Smart Grid Telemetry.
    Trained on normal grid operating conditions to detect unknown or unusual behavioral drift.
    """

    FEATURE_NAMES = [
        "v_ratio",         # voltage / nominal_voltage
        "i_ratio",         # current / nominal_current
        "f_ratio",         # frequency / 50.0
        "p_ratio",         # power / nominal_power
        "latency",         # ms
        "packet_rate",     # pkts/s
        "packet_loss",     # %
        "failed_logins",   # count
    ]

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model: Optional[IsolationForest] = None
        self.is_trained: bool = False
        self.baseline_stats: Dict[str, Dict[str, float]] = {}

        if SKLEARN_AVAILABLE:
            if model_path and os.path.exists(model_path):
                try:
                    self.model = joblib.load(model_path)
                    self.is_trained = True
                except Exception:
                    self._train_and_save()
            else:
                self._train_and_save()
        else:
            self._fit_statistical_baseline()

    def _extract_feature_vector(self, telem: DeviceTelemetry, nominals: Dict[str, float]) -> np.ndarray:
        """
        Extract normalized 8-dimensional feature vector:
        Relative ratios allow unified detection across 230V meters and 33kV substations.
        """
        nom_v = nominals.get("nominal_v", 230.0)
        nom_i = nominals.get("nominal_i", 20.0)
        nom_f = nominals.get("nominal_f", 50.0)
        nom_p = nominals.get("nominal_p", 5.0)

        v_ratio = telem.voltage / nom_v if nom_v > 0 else 1.0
        i_ratio = telem.current / nom_i if nom_i > 0 else 1.0
        f_ratio = telem.frequency / nom_f if nom_f > 0 else 1.0
        p_ratio = telem.power / nom_p if nom_p > 0 else 1.0

        return np.array([
            v_ratio,
            i_ratio,
            f_ratio,
            p_ratio,
            telem.network_latency,
            telem.packet_rate,
            telem.packet_loss,
            float(telem.failed_login_attempts),
        ], dtype=float)

    def _generate_normal_training_data(self, n_samples: int = 1500) -> np.ndarray:
        """
        Synthesize realistic normal operating telemetry samples with fixed seed.
        """
        np.random.seed(42)
        random.seed(42)

        # Normal distributions around nominal baseline (1.0 ratio ± 1.5%)
        v_ratios = np.random.normal(1.0, 0.015, n_samples)
        i_ratios = np.random.normal(1.0, 0.025, n_samples)
        f_ratios = np.random.normal(1.0, 0.002, n_samples) # ±0.1 Hz
        p_ratios = np.random.normal(1.0, 0.025, n_samples)

        # Latency typically 10-25 ms with occasional small jitter
        latencies = np.random.gamma(shape=3.0, scale=5.0, size=n_samples) + 5.0

        # Packet rates 50-350 pkts/s
        packet_rates = np.random.uniform(50.0, 350.0, n_samples)

        # Packet loss 0.0% to 0.4%
        packet_losses = np.random.exponential(scale=0.1, size=n_samples)
        packet_losses = np.clip(packet_losses, 0.0, 0.5)

        # Failed logins: 0 in normal operation
        failed_logins = np.zeros(n_samples, dtype=float)

        X = np.column_stack([
            v_ratios,
            i_ratios,
            f_ratios,
            p_ratios,
            latencies,
            packet_rates,
            packet_losses,
            failed_logins,
        ])
        return X

    def _train_and_save(self):
        """Train scikit-learn Isolation Forest and persist model to disk."""
        if not SKLEARN_AVAILABLE:
            return

        X_train = self._generate_normal_training_data(n_samples=2000)
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.04,
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X_train)
        self.is_trained = True

        if self.model_path:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)

    def _fit_statistical_baseline(self):
        """Statistical fallback when scikit-learn is not available in environment."""
        self.baseline_stats = {
            "v_ratio": {"mean": 1.0, "std": 0.02},
            "i_ratio": {"mean": 1.0, "std": 0.03},
            "f_ratio": {"mean": 1.0, "std": 0.003},
            "p_ratio": {"mean": 1.0, "std": 0.03},
            "latency": {"mean": 18.0, "std": 8.0},
            "packet_rate": {"mean": 150.0, "std": 80.0},
            "packet_loss": {"mean": 0.15, "std": 0.15},
            "failed_logins": {"mean": 0.0, "std": 0.5},
        }

    def predict(self, telem: DeviceTelemetry, nominals: Dict[str, float]) -> Tuple[bool, float]:
        """
        Evaluate if telemetry point is an anomaly.
        Returns:
            anomaly_detected (bool): True if unusual behavior detected
            anomaly_score (float): Normalized score [0.0 to 1.0], where > 0.60 indicates anomaly
        """
        x = self._extract_feature_vector(telem, nominals).reshape(1, -1)

        if SKLEARN_AVAILABLE and self.model is not None and self.is_trained:
            # IsolationForest decision_function: lower means more anomalous (negative = anomaly)
            raw_score = self.model.decision_function(x)[0]
            # Convert decision function to normalized anomaly score between 0.0 and 1.0
            # raw_score ranges typically from -0.3 (extreme anomaly) to +0.25 (typical normal)
            norm_score = max(0.0, min(1.0, 0.5 - raw_score * 2.0))
            is_anomaly = bool(self.model.predict(x)[0] == -1 or norm_score >= 0.58)
            return is_anomaly, round(norm_score, 3)

        # Statistical fallback
        vec = x[0]
        z_scores = [
            abs(vec[0] - 1.0) / 0.02,
            abs(vec[1] - 1.0) / 0.03,
            abs(vec[2] - 1.0) / 0.003,
            abs(vec[3] - 1.0) / 0.03,
            max(0.0, (vec[4] - 25.0) / 10.0),
            max(0.0, (vec[5] - 350.0) / 100.0),
            max(0.0, (vec[6] - 0.5) / 0.5),
            vec[7] * 2.5,
        ]
        max_z = max(z_scores)
        score = min(1.0, max_z / 4.0)
        is_anom = score >= 0.55
        return is_anom, round(score, 3)
