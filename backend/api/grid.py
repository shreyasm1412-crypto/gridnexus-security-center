from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from ..models.schemas import DeviceTelemetry, GridNodeSchema
from ..state import twin

router = APIRouter(prefix="/grid", tags=["Smart Grid"])

@router.get("/live-data", response_model=List[DeviceTelemetry])
def get_live_data() -> List[DeviceTelemetry]:
    """Get live electrical and network telemetry for all 10 smart grid devices."""
    return twin.get_all_telemetry()

@router.get("/devices", response_model=List[GridNodeSchema])
def get_devices() -> List[GridNodeSchema]:
    """Get all 10 smart grid nodes formatted with engineering display units."""
    return twin.get_grid_nodes()

@router.get("/devices/{device_id}", response_model=GridNodeSchema)
def get_device(device_id: str) -> GridNodeSchema:
    """Get single smart grid node by ID."""
    nodes = twin.get_grid_nodes()
    for n in nodes:
        if n.id.upper() == device_id.upper():
            return n
    raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

@router.get("/topology")
def get_topology() -> Dict[str, Any]:
    """
    Get digital twin topology:
    Returns 10 nodes and 9 interconnecting transmission/distribution edges.
    """
    nodes = twin.get_grid_nodes()
    edges = [
        ["PS-01", "SUB-01"],
        ["SUB-01", "FDR-A"],
        ["SUB-01", "FDR-B"],
        ["FDR-A", "SM-01"],
        ["FDR-A", "SM-02"],
        ["FDR-A", "SM-03"],
        ["FDR-B", "SM-04"],
        ["FDR-B", "SM-05"],
        ["FDR-B", "SM-06"],
    ]
    return {
        "nodes": [n.model_dump() for n in nodes],
        "edges": edges,
        "attack_mode": twin.attack_mode,
        "attack_target": twin.attack_target,
    }
