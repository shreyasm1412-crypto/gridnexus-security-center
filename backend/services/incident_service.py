from datetime import datetime
from typing import List, Optional, Dict, Literal
from ..models.schemas import (
    IncidentSchema,
    IncidentTimelineEvent,
    IncidentStatus,
    SeverityLevel,
    ThreatType,
)
from .response_engine import SimulatedResponseEngine

STAGE_ORDER: List[IncidentStatus] = ["Open", "Investigating", "Contained", "Resolved"]
STAGE_NAMES = ["Detected", "Analyzed", "Contained", "Resolved"]

class IncidentService:
    """
    In-memory Incident Management Service.
    Automates creation and tracks lifecycle progression of smart grid cybersecurity incidents.
    """

    def __init__(self):
        self._incidents: List[IncidentSchema] = [
            IncidentSchema(
                id="INC-0117",
                type="False Data Injection",
                device="SM-04",
                severity="HIGH",
                time="2026-11-02 13:21",
                risk=78,
                status="Investigating",
                timeline=[
                    IncidentTimelineEvent(stage="Detected", time="13:21:44", completed=True),
                    IncidentTimelineEvent(stage="Analyzed", time="13:22:10", completed=True),
                    IncidentTimelineEvent(stage="Contained", time="--", completed=False),
                    IncidentTimelineEvent(stage="Resolved", time="--", completed=False),
                ],
                recommended_response=SimulatedResponseEngine.get_recommended_response("False Data Injection"),
            ),
            IncidentSchema(
                id="INC-0116",
                type="Unauthorized Access",
                device="SUB-01",
                severity="HIGH",
                time="2026-11-02 12:05",
                risk=71,
                status="Open",
                timeline=[
                    IncidentTimelineEvent(stage="Detected", time="12:05:02", completed=True),
                    IncidentTimelineEvent(stage="Analyzed", time="--", completed=False),
                    IncidentTimelineEvent(stage="Contained", time="--", completed=False),
                    IncidentTimelineEvent(stage="Resolved", time="--", completed=False),
                ],
                recommended_response=SimulatedResponseEngine.get_recommended_response("Unauthorized Access"),
            ),
            IncidentSchema(
                id="INC-0115",
                type="Denial of Service",
                device="FDR-B",
                severity="MEDIUM",
                time="2026-11-02 10:48",
                risk=54,
                status="Contained",
                timeline=[
                    IncidentTimelineEvent(stage="Detected", time="10:48:12", completed=True),
                    IncidentTimelineEvent(stage="Analyzed", time="10:49:00", completed=True),
                    IncidentTimelineEvent(stage="Contained", time="10:55:18", completed=True),
                    IncidentTimelineEvent(stage="Resolved", time="--", completed=False),
                ],
                recommended_response=SimulatedResponseEngine.get_recommended_response("Denial of Service"),
            ),
            IncidentSchema(
                id="INC-0114",
                type="False Data Injection",
                device="SM-06",
                severity="MEDIUM",
                time="2026-11-01 22:16",
                risk=46,
                status="Resolved",
                timeline=[
                    IncidentTimelineEvent(stage="Detected", time="22:16:05", completed=True),
                    IncidentTimelineEvent(stage="Analyzed", time="22:17:30", completed=True),
                    IncidentTimelineEvent(stage="Contained", time="22:25:00", completed=True),
                    IncidentTimelineEvent(stage="Resolved", time="22:40:12", completed=True),
                ],
                recommended_response=SimulatedResponseEngine.get_recommended_response("False Data Injection"),
            ),
            IncidentSchema(
                id="INC-0113",
                type="Denial of Service",
                device="FDR-A",
                severity="LOW",
                time="2026-11-01 17:39",
                risk=28,
                status="Resolved",
                timeline=[
                    IncidentTimelineEvent(stage="Detected", time="17:39:00", completed=True),
                    IncidentTimelineEvent(stage="Analyzed", time="17:40:15", completed=True),
                    IncidentTimelineEvent(stage="Contained", time="17:48:00", completed=True),
                    IncidentTimelineEvent(stage="Resolved", time="17:55:30", completed=True),
                ],
                recommended_response=SimulatedResponseEngine.get_recommended_response("Denial of Service"),
            ),
        ]
        self._next_incident_num = 118

    def get_all(self) -> List[IncidentSchema]:
        return self._incidents

    def get_by_id(self, incident_id: str) -> Optional[IncidentSchema]:
        for inc in self._incidents:
            if inc.id == incident_id:
                return inc
        return None

    def create_incident(
        self,
        threat_type: Literal["False Data Injection", "Denial of Service", "Unauthorized Access"],
        device: str,
        severity: SeverityLevel,
        risk: int,
        status: IncidentStatus = "Open",
    ) -> IncidentSchema:
        incident_id = f"INC-0{self._next_incident_num}"
        self._next_incident_num += 1
        now_dt = datetime.now()
        now_str = now_dt.strftime("%Y-%m-%d %H:%M")
        now_time = now_dt.strftime("%H:%M:%S")

        timeline = [
            IncidentTimelineEvent(stage="Detected", time=now_time, completed=True),
            IncidentTimelineEvent(stage="Analyzed", time=now_time if status in ["Investigating", "Contained", "Resolved"] else "--", completed=status in ["Investigating", "Contained", "Resolved"]),
            IncidentTimelineEvent(stage="Contained", time=now_time if status in ["Contained", "Resolved"] else "--", completed=status in ["Contained", "Resolved"]),
            IncidentTimelineEvent(stage="Resolved", time=now_time if status == "Resolved" else "--", completed=status == "Resolved"),
        ]

        responses = SimulatedResponseEngine.get_recommended_response(threat_type)

        incident = IncidentSchema(
            id=incident_id,
            type=threat_type,
            device=device,
            severity=severity,
            time=now_str,
            risk=risk,
            status=status,
            timeline=timeline,
            recommended_response=responses,
        )
        self._incidents.insert(0, incident)
        return incident

    def update_status(self, incident_id: str, new_status: IncidentStatus) -> Optional[IncidentSchema]:
        inc = self.get_by_id(incident_id)
        if not inc:
            return None

        inc.status = new_status
        now_time = datetime.now().strftime("%H:%M:%S")
        status_idx = STAGE_ORDER.index(new_status)

        # Update timeline events
        for idx, event in enumerate(inc.timeline):
            if idx <= status_idx:
                event.completed = True
                if event.time == "--":
                    event.time = now_time
            else:
                event.completed = False
                event.time = "--"

        return inc

    def reset_to_initial(self):
        self.__init__()
