from typing import List
from fastapi import APIRouter, HTTPException
from ..models.schemas import AlertSchema
from ..state import alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertSchema])
def get_alerts(limit: int = 50) -> List[AlertSchema]:
    """Get active and historical cyber defense alerts."""
    return alert_service.get_all(limit=limit)

@router.get("/{alert_id}", response_model=AlertSchema)
def get_alert(alert_id: str) -> AlertSchema:
    """Get detailed information and explainable AI evidence for a specific alert."""
    alert = alert_service.get_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return alert
