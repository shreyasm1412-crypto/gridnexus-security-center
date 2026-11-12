from typing import List
from fastapi import APIRouter, HTTPException
from ..models.schemas import IncidentSchema, IncidentStatusUpdate
from ..state import incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentSchema])
def get_incidents() -> List[IncidentSchema]:
    """Get all smart grid security incidents and lifecycle states."""
    return incident_service.get_all()

@router.get("/{incident_id}", response_model=IncidentSchema)
def get_incident(incident_id: str) -> IncidentSchema:
    """Get detailed lifecycle and timeline for a specific incident."""
    inc = incident_service.get_by_id(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return inc

@router.patch("/{incident_id}/status", response_model=IncidentSchema)
def update_incident_status(incident_id: str, payload: IncidentStatusUpdate) -> IncidentSchema:
    """
    Transition incident lifecycle state:
    Open -> Investigating -> Contained -> Resolved.
    Updates the incident timeline and audit logs.
    """
    updated = incident_service.update_status(incident_id, payload.status)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return updated
