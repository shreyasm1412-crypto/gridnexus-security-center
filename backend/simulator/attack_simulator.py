from typing import Dict, Any, Tuple
from ..models.schemas import AttackKey
from .grid_simulator import SmartGridDigitalTwin

class AttackSimulator:
    """
    Orchestrates safe software-only cyberattack simulations on the Smart Grid Digital Twin.
    """

    def __init__(self, twin: SmartGridDigitalTwin):
        self.twin = twin
        self.active_mode: AttackKey = "normal"
        self.scenarios: Dict[AttackKey, Dict[str, Any]] = {
            "normal": {
                "title": "Normal Operation",
                "description": "Return the simulated grid to a stable operational state.",
                "stage": 0,
                "grid_health": 96,
                "latency": 12,
                "confidence": 0,
                "risk": 12,
                "target": None,
            },
            "fdi": {
                "title": "False Data Injection",
                "description": "Manipulates reported electrical telemetry data to cause power balance distortion.",
                "stage": 5,
                "grid_health": 72,
                "latency": 48,
                "confidence": 94,
                "risk": 92,
                "target": "SM-04",
            },
            "dos": {
                "title": "Denial of Service",
                "description": "Simulates communication overload and severe network latency degradation.",
                "stage": 4,
                "grid_health": 81,
                "latency": 286,
                "confidence": 88,
                "risk": 74,
                "target": "FDR-B",
            },
            "ua": {
                "title": "Unauthorized Access",
                "description": "Simulates suspicious access and brute-force credential attempts on critical SCADA interface.",
                "stage": 3,
                "grid_health": 89,
                "latency": 21,
                "confidence": 83,
                "risk": 81,
                "target": "SUB-01",
            },
        }

    def trigger_normal(self) -> Dict[str, Any]:
        """Reset digital twin to normal operating conditions."""
        self.active_mode = "normal"
        self.twin.reset_to_normal()
        return self.scenarios["normal"]

    def trigger_fdi(self) -> Dict[str, Any]:
        """
        Simulate False Data Injection targeting SM-04.
        Injects anomalous voltage (+24%), inflated power (+270%), and altered frequency.
        """
        self.active_mode = "fdi"
        target = "SM-04"
        overrides = {
            target: {
                "voltage": 288.6,            # Normal ~231.2 V (severe +24.8% spike)
                "power": 18.5,               # Normal ~5.0 kW (severe +270% inflation)
                "current": 64.2,             # Normal ~21.9 A
                "frequency": 50.48,          # Abnormal frequency reading
                "network_latency": 48.0,     # Moderately elevated latency
                "status": "threat",
            },
            "FDR-B": {
                "status": "warning",         # Feeder detects power mismatch across child meters
            },
        }
        self.twin.set_attack_mode("fdi", target, overrides)
        return self.scenarios["fdi"]

    def trigger_dos(self) -> Dict[str, Any]:
        """
        Simulate Denial of Service targeting FDR-B (Feeder B).
        Floods network interface with malformed packets, spikes latency to 286 ms, packet loss 28.5%.
        """
        self.active_mode = "dos"
        target = "FDR-B"
        overrides = {
            target: {
                "packet_rate": 3420.0,       # Normal ~255 pkts/s (13.4x flood)
                "network_latency": 286.0,    # Normal ~13 ms (severe 22x latency spike)
                "packet_loss": 28.5,         # Normal ~0.10% (high packet drop rate)
                "status": "threat",
            },
            "SUB-01": {
                "status": "warning",         # Substation communication link degraded
            },
        }
        self.twin.set_attack_mode("dos", target, overrides)
        return self.scenarios["dos"]

    def trigger_unauthorized_access(self) -> Dict[str, Any]:
        """
        Simulate Unauthorized Access targeting SUB-01 (Main Substation).
        Rapid burst of 16 failed credential attempts against SCADA management terminal.
        """
        self.active_mode = "ua"
        target = "SUB-01"
        overrides = {
            target: {
                "failed_login_attempts": 16, # Repeated authentication failures
                "network_latency": 21.0,     # Slightly elevated connection latency
                "packet_rate": 680.0,        # Suspicious authentication probe bursts
                "status": "threat",
            },
        }
        self.twin.set_attack_mode("ua", target, overrides)
        return self.scenarios["ua"]

    def get_current_scenario(self) -> Dict[str, Any]:
        return self.scenarios[self.active_mode]
