from typing import Dict, List, Tuple
from ..models.schemas import DeviceTelemetry

class RuleBasedDetectionEngine:
    """
    Deterministic rule-based smart grid cyber threat detection layer.
    Evaluates physical electrical bounds, network metrics, and access security telemetry.
    """

    def __init__(self):
        # Configurable operational thresholds
        self.voltage_deviation_threshold_pct = 6.0  # % deviation from nominal
        self.freq_min = 49.70                       # Hz
        self.freq_max = 50.30                       # Hz
        self.smart_meter_power_max_kw = 10.0        # kW max normal meter consumption
        self.latency_warn_ms = 60.0                 # ms
        self.latency_critical_ms = 120.0            # ms
        self.packet_rate_spike_multiplier = 3.5     # relative to baseline
        self.packet_loss_critical_pct = 5.0         # %
        self.failed_login_warn = 3                  # attempts
        self.failed_login_critical = 8              # attempts

    def evaluate(self, telem: DeviceTelemetry, nominal_voltage: float = 230.0) -> Dict:
        """
        Evaluate device telemetry against cybersecurity and electrical rules.
        Returns:
            suspicious: bool
            triggered_rules: List[str]
            evidence: List[str]
            category_scores: Dict[str, float]
        """
        triggered_rules: List[str] = []
        evidence: List[str] = []
        scores = {
            "False Data Injection": 0.0,
            "Denial of Service": 0.0,
            "Unauthorized Access": 0.0,
        }

        # -------------------------------------------------------------
        # 1. Electrical Telemetry Rules (FDI Indicators)
        # -------------------------------------------------------------
        if nominal_voltage > 0:
            v_dev_pct = abs(telem.voltage - nominal_voltage) / nominal_voltage * 100.0
            if v_dev_pct > self.voltage_deviation_threshold_pct:
                rule_msg = f"RULE_ELEC_VOLTAGE_OUT_OF_BOUNDS: Voltage reading deviates {v_dev_pct:.1f}% from nominal baseline"
                triggered_rules.append(rule_msg)
                evidence.append(f"Voltage reading ({telem.voltage:.1f} V) deviates {v_dev_pct:.1f}% from baseline (threshold ±{self.voltage_deviation_threshold_pct}%)")
                scores["False Data Injection"] += min(45.0, v_dev_pct * 1.8)

        if telem.frequency < self.freq_min or telem.frequency > self.freq_max:
            rule_msg = f"RULE_ELEC_FREQUENCY_ABNORMAL: Frequency {telem.frequency:.2f} Hz exceeds operational window [{self.freq_min}-{self.freq_max} Hz]"
            triggered_rules.append(rule_msg)
            evidence.append(f"Grid frequency irregularity recorded at {telem.frequency:.2f} Hz")
            scores["False Data Injection"] += 30.0

        if telem.device_type == "Smart Meter" and telem.power > self.smart_meter_power_max_kw:
            rule_msg = f"RULE_ELEC_POWER_MISMATCH: Meter power {telem.power:.1f} kW exceeds plausible load limit ({self.smart_meter_power_max_kw} kW)"
            triggered_rules.append(rule_msg)
            evidence.append(f"Power consumption mismatch of {telem.power:.1f} kW across feeder segment")
            scores["False Data Injection"] += 35.0

        # -------------------------------------------------------------
        # 2. Network Telemetry Rules (DoS Indicators)
        # -------------------------------------------------------------
        if telem.packet_rate > 1000.0:
            rule_msg = f"RULE_NET_PACKET_FLOOD: Packet arrival rate ({telem.packet_rate:.0f} pkts/s) indicates volumetric flood"
            triggered_rules.append(rule_msg)
            evidence.append(f"Packet ingestion rate {telem.packet_rate:.0f} pkts/s is over 10x above normal baseline")
            scores["Denial of Service"] += 45.0

        if telem.network_latency > self.latency_critical_ms:
            rule_msg = f"RULE_NET_LATENCY_SPIKE: Severe network round-trip delay ({telem.network_latency:.0f} ms > {self.latency_critical_ms} ms)"
            triggered_rules.append(rule_msg)
            evidence.append(f"Network latency surged from baseline to {telem.network_latency:.0f} ms")
            scores["Denial of Service"] += 40.0
        elif telem.network_latency > self.latency_warn_ms:
            triggered_rules.append(f"RULE_NET_LATENCY_ELEVATED: Elevated delay ({telem.network_latency:.0f} ms)")
            scores["Denial of Service"] += 15.0

        if telem.packet_loss > self.packet_loss_critical_pct:
            rule_msg = f"RULE_NET_PACKET_DROP: High communication packet loss ({telem.packet_loss:.1f}% > {self.packet_loss_critical_pct}%)"
            triggered_rules.append(rule_msg)
            evidence.append(f"Network communication dropping {telem.packet_loss:.1f}% of control packets")
            scores["Denial of Service"] += 30.0

        # -------------------------------------------------------------
        # 3. Security Access Rules (Unauthorized Access Indicators)
        # -------------------------------------------------------------
        if telem.failed_login_attempts >= self.failed_login_critical:
            rule_msg = f"RULE_SEC_BRUTE_FORCE: High frequency failed logins ({telem.failed_login_attempts} attempts)"
            triggered_rules.append(rule_msg)
            evidence.append(f"{telem.failed_login_attempts} repeated failed authentication attempts recorded in rapid succession")
            scores["Unauthorized Access"] += 60.0
        elif telem.failed_login_attempts >= self.failed_login_warn:
            rule_msg = f"RULE_SEC_FAILED_AUTH: Suspicious login failures ({telem.failed_login_attempts} attempts)"
            triggered_rules.append(rule_msg)
            evidence.append(f"{telem.failed_login_attempts} failed login attempts against node management interface")
            scores["Unauthorized Access"] += 30.0

        if telem.device_type in ["Substation", "Power Source"] and telem.failed_login_attempts > 0:
            triggered_rules.append("RULE_SEC_CRITICAL_ASSET_PROBE: Authentication challenge failure on Tier-1 critical asset")
            evidence.append("Security event originated directly on critical SCADA control terminal")
            scores["Unauthorized Access"] += 25.0

        suspicious = len(triggered_rules) > 0
        return {
            "suspicious": suspicious,
            "triggered_rules": triggered_rules,
            "evidence": evidence,
            "category_scores": scores,
        }
