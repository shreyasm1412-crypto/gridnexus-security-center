from typing import List
from ..models.schemas import ThreatType

class SimulatedResponseEngine:
    """
    Generates safe, simulated mitigation and incident response playbooks.
    Note: These actions are simulated cybersecurity countermeasures and do not
    execute physical commands or touch actual grid hardware.
    """

    RESPONSES = {
        "False Data Injection": [
            "Flag suspicious telemetry",
            "Isolate affected device",
            "Switch to trusted telemetry",
        ],
        "Denial of Service": [
            "Limit suspicious traffic",
            "Prioritize critical communication",
            "Generate security alert",
        ],
        "Unauthorized Access": [
            "Terminate suspicious session",
            "Lock affected access",
            "Escalate the incident",
        ],
        "Unknown Anomaly": [
            "Monitor device for recurrence",
            "Verify firmware integrity",
            "Close after observation window",
        ],
        "Normal": [
            "Routine telemetry verification",
            "Continuous anomaly observation",
        ],
    }

    @classmethod
    def get_recommended_response(cls, threat_type: ThreatType) -> List[str]:
        return cls.RESPONSES.get(threat_type, [
            "Engage SOC Tier-2 analyst",
            "Verify telemetry integrity",
            "Maintain operational log",
        ])
