import os
import random
from typing import Dict, Tuple, List, Optional
import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    RandomForestClassifier = None
    joblib = None

from ..models.schemas import DeviceTelemetry

class RandomForestAttackClassifier:
    """
    Genuine scikit-learn Random Forest classifier for Smart Grid Cyberattacks.
    Trained on reproducible synthetic dataset covering:
    - Normal
    - False Data Injection (FDI)
    - Denial of Service (DoS)
    - Unauthorized Access (UA)
    """

    CLASSES = [
        "Normal",
        "False Data Injection",
        "Denial of Service",
        "Unauthorized Access",
    ]

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model: Optional[RandomForestClassifier] = None
        self.is_trained: bool = False

        if SKLEARN_AVAILABLE:
            if model_path and os.path.exists(model_path):
                try:
                    self.model = joblib.load(model_path)
                    self.is_trained = True
                except Exception:
                    self._train_and_save()
            else:
                self._train_and_save()

    def _extract_feature_vector(self, telem: DeviceTelemetry, nominals: Dict[str, float]) -> np.ndarray:
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

    def _generate_synthetic_dataset(self, n_per_class: int = 500) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate reproducible, balanced synthetic training dataset for all 4 classes.
        Fixed seed = 42 ensures exact determinism.
        """
        np.random.seed(42)
        random.seed(42)

        X_list: List[np.ndarray] = []
        y_list: List[int] = []

        # -------------------------------------------------------------
        # Class 0: Normal
        # -------------------------------------------------------------
        v0 = np.random.normal(1.0, 0.015, n_per_class)
        i0 = np.random.normal(1.0, 0.02, n_per_class)
        f0 = np.random.normal(1.0, 0.002, n_per_class)
        p0 = np.random.normal(1.0, 0.02, n_per_class)
        lat0 = np.random.uniform(8.0, 26.0, n_per_class)
        pkt0 = np.random.uniform(50.0, 350.0, n_per_class)
        loss0 = np.random.uniform(0.0, 0.3, n_per_class)
        logins0 = np.zeros(n_per_class, dtype=float)
        X0 = np.column_stack([v0, i0, f0, p0, lat0, pkt0, loss0, logins0])
        X_list.append(X0)
        y_list.extend([0] * n_per_class)

        # -------------------------------------------------------------
        # Class 1: False Data Injection (Manipulated electrical signals)
        # -------------------------------------------------------------
        v1_choice = np.random.choice([1.20, 0.80], size=n_per_class) + np.random.normal(0, 0.04, n_per_class)
        i1 = np.random.uniform(1.8, 3.5, n_per_class)
        f1 = np.random.choice([1.01, 0.99], size=n_per_class) + np.random.normal(0, 0.003, n_per_class)
        p1 = np.random.uniform(2.5, 4.5, n_per_class)  # High power mismatch
        lat1 = np.random.uniform(25.0, 55.0, n_per_class)
        pkt1 = np.random.uniform(60.0, 180.0, n_per_class)
        loss1 = np.random.uniform(0.1, 0.8, n_per_class)
        logins1 = np.zeros(n_per_class, dtype=float)
        X1 = np.column_stack([v1_choice, i1, f1, p1, lat1, pkt1, loss1, logins1])
        X_list.append(X1)
        y_list.extend([1] * n_per_class)

        # -------------------------------------------------------------
        # Class 2: Denial of Service (Communication flood & degradation)
        # -------------------------------------------------------------
        v2 = np.random.normal(1.0, 0.015, n_per_class)
        i2 = np.random.normal(1.0, 0.02, n_per_class)
        f2 = np.random.normal(1.0, 0.002, n_per_class)
        p2 = np.random.normal(1.0, 0.02, n_per_class)
        lat2 = np.random.uniform(180.0, 380.0, n_per_class) # High latency
        pkt2 = np.random.uniform(2000.0, 4500.0, n_per_class) # Massive flood
        loss2 = np.random.uniform(15.0, 40.0, n_per_class) # High loss
        logins2 = np.zeros(n_per_class, dtype=float)
        X2 = np.column_stack([v2, i2, f2, p2, lat2, pkt2, loss2, logins2])
        X_list.append(X2)
        y_list.extend([2] * n_per_class)

        # -------------------------------------------------------------
        # Class 3: Unauthorized Access (Authentication brute-force)
        # -------------------------------------------------------------
        v3 = np.random.normal(1.0, 0.015, n_per_class)
        i3 = np.random.normal(1.0, 0.02, n_per_class)
        f3 = np.random.normal(1.0, 0.002, n_per_class)
        p3 = np.random.normal(1.0, 0.02, n_per_class)
        lat3 = np.random.uniform(15.0, 35.0, n_per_class)
        pkt3 = np.random.uniform(400.0, 900.0, n_per_class) # Authentication probe bursts
        loss3 = np.random.uniform(0.1, 0.9, n_per_class)
        logins3 = np.random.randint(6, 25, size=n_per_class).astype(float)
        X3 = np.column_stack([v3, i3, f3, p3, lat3, pkt3, loss3, logins3])
        X_list.append(X3)
        y_list.extend([3] * n_per_class)

        X = np.vstack(X_list)
        y = np.array(y_list)
        return X, y

    def _train_and_save(self):
        if not SKLEARN_AVAILABLE:
            return

        X_train, y_train = self._generate_synthetic_dataset(n_per_class=500)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            random_state=42,
            n_jobs=-1,
        )
        self.model.fit(X_train, y_train)
        self.is_trained = True

        if self.model_path:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)

    def predict(self, telem: DeviceTelemetry, nominals: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        """
        Classify smart grid telemetry sample.
        Returns:
            predicted_class (str): One of the 4 classes
            confidence (float): 0.0 to 100.0
            probabilities (Dict[str, float]): per-class confidence percentages
        """
        x = self._extract_feature_vector(telem, nominals).reshape(1, -1)

        if SKLEARN_AVAILABLE and self.model is not None and self.is_trained:
            probs = self.model.predict_proba(x)[0]
            pred_idx = int(np.argmax(probs))
            predicted_class = self.CLASSES[pred_idx]
            confidence = round(float(probs[pred_idx]) * 100.0, 1)

            prob_dict = {
                self.CLASSES[i]: round(float(probs[i]) * 100.0, 1)
                for i in range(len(self.CLASSES))
            }
            return predicted_class, confidence, prob_dict

        # Deterministic feature rule matching fallback
        vec = x[0]
        # Check UA
        if vec[7] >= 3.0:
            conf = min(98.0, 75.0 + vec[7] * 1.5)
            return "Unauthorized Access", round(conf, 1), {
                "Normal": 2.0, "False Data Injection": 3.0, "Denial of Service": 5.0, "Unauthorized Access": conf
            }
        # Check DoS
        if vec[5] > 1200.0 or vec[4] > 120.0:
            conf = min(96.0, 80.0 + (vec[4] / 300.0) * 15.0)
            return "Denial of Service", round(conf, 1), {
                "Normal": 3.0, "False Data Injection": 4.0, "Denial of Service": conf, "Unauthorized Access": 3.0
            }
        # Check FDI
        if abs(vec[0] - 1.0) > 0.06 or vec[3] > 2.0:
            conf = min(96.0, 84.0 + abs(vec[0] - 1.0) * 50.0)
            return "False Data Injection", round(conf, 1), {
                "Normal": 3.0, "False Data Injection": conf, "Denial of Service": 2.0, "Unauthorized Access": 2.0
            }

        return "Normal", 98.5, {
            "Normal": 98.5, "False Data Injection": 0.5, "Denial of Service": 0.5, "Unauthorized Access": 0.5
        }
