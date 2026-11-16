from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from ..database import connection
from ..services import persistent_service as service
from ..models.schemas import IncidentStatusUpdate

router = APIRouter(prefix="/api")


class SimulationInput(BaseModel):
    device_id: str = Field(default="SM-04", min_length=4, max_length=10, pattern=r"^[A-Z0-9-]+$")
    attack: Literal["normal", "fdi", "dos", "ua"] = "normal"
    request_id: str | None = Field(default=None, max_length=64)


@router.get("/snapshot")
def snapshot():
    return service.snapshot()


@router.get("/dashboard")
def dashboard():
    from .dashboard import get_dashboard
    result = get_dashboard().model_dump()
    stored = service.snapshot()
    result.update(stored["dashboard"])
    active = stored["simulation"]
    result.update(active_attack=active["mode"] if active else "normal", active_target=active["target"] if active else None)
    return result


@router.get("/grid/live-data")
def live_data():
    return service.snapshot()["telemetry"]


@router.get("/grid/devices")
def devices():
    from ..state import twin
    data = service.snapshot()
    def format_node(t):
        spec = twin.device_specs[t["device_id"]]
        voltage = f'{t["voltage"] / 1000:.1f} kV' if spec["display_unit_v"] == "kV" else f'{t["voltage"]:.1f} V'
        power = f'{t["power"] / 1000:.1f} MW' if spec["display_unit_p"] == "MW" else f'{t["power"]:.1f} kW'
        return dict(id=t["device_id"], label=t["device_name"], type=t["device_type"], status=t["status"], voltage=voltage,
                    power=power, current=f'{t["current"]:,.1f} A', frequency=f'{t["frequency"]:.2f} Hz', latency=round(t["network_latency"]),
                    risk=data["simulation"]["risk"] if data["simulation"] and data["simulation"]["target"] == t["device_id"] else 12,
                    telemetry=t)
    return [format_node(t) for t in data["telemetry"]]


@router.get("/grid/devices/{device_id}")
def device(device_id: str):
    found = next((d for d in devices() if d["id"] == device_id.upper()), None)
    if not found:
        raise HTTPException(404, "Device not found")
    return found


@router.get("/grid/devices/{device_id}/telemetry")
def device_telemetry(device_id: str, limit: int = Query(50, ge=1, le=500)):
    device(device_id)
    with connection() as db:
        return [dict(r) for r in db.execute("SELECT * FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT ?", (device_id.upper(), limit))]


@router.get("/grid/topology")
def topology():
    from ..state import twin
    data = service.snapshot()["simulation"]
    return dict(nodes=devices(), edges=[[p, c] for c, p in twin.parents.items() if p],
                attack_mode=data["mode"] if data else "normal", attack_target=data["target"] if data else None)


@router.post("/simulation/start")
def start(payload: SimulationInput):
    return service.run(payload.attack, payload.device_id, payload.request_id)


@router.post("/simulation/reset")
@router.post("/simulation/normal")
def reset(payload: SimulationInput = SimulationInput()):
    return service.run("normal", payload.device_id, payload.request_id)


@router.post("/simulation/{mode}")
def legacy_start(mode: Literal["fdi", "dos", "unauthorized-access"], payload: SimulationInput | None = None):
    attack = "ua" if mode == "unauthorized-access" else mode
    target = payload.device_id if payload else {"fdi": "SM-04", "dos": "FDR-B", "ua": "SUB-01"}[attack]
    return service.run(attack, target, payload.request_id if payload else None)


@router.get("/simulation/status")
def simulation_status():
    data = service.snapshot()["simulation"]
    return dict(mode=data["mode"] if data else "normal", scenario=data)


@router.get("/simulation/history")
def history(limit: int = Query(50, ge=1, le=500)):
    with connection() as db:
        return [dict(r) for r in db.execute("SELECT id,target_device,attack_type,status,start_time,end_time FROM simulation_history ORDER BY rowid DESC LIMIT ?", (limit,))]


@router.get("/alerts")
def alerts(limit: int = Query(50, ge=1, le=500)):
    return service.snapshot()["alerts"][:limit]


@router.get("/alerts/{alert_id}")
@router.get("/alerts/{alert_id}/explainability")
def alert(alert_id: str):
    found = next((a for a in service.snapshot()["alerts"] if a["id"] == alert_id), None)
    if not found:
        raise HTTPException(404, "Alert not found")
    return found


@router.get("/incidents")
def incidents():
    return service.snapshot()["incidents"]


@router.get("/incidents/{incident_id}")
def incident(incident_id: str):
    found = next((i for i in incidents() if i["id"] == incident_id), None)
    if not found:
        raise HTTPException(404, "Incident not found")
    return found


class IncidentInput(BaseModel):
    alert_id: str = Field(min_length=1, max_length=64)


@router.post("/incidents")
def create_incident(payload: IncidentInput):
    a = alert(payload.alert_id)
    if a["type"] == "Unknown Anomaly":
        raise HTTPException(422, "Unclassified anomalies cannot create classified incidents")
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        import json
        from uuid import uuid4
        existing = db.execute("SELECT payload FROM incidents WHERE alert_id=?", (payload.alert_id,)).fetchone()
        if existing:
            return json.loads(existing[0])
        item = dict(id="INC-" + uuid4().hex[:12], type=a["type"], device=a["device"], severity=a["severity"], risk=a["risk"],
                    status="Open", time=service.now(), timeline=[dict(stage=s, time=service.now() if idx == 0 else "--", completed=idx == 0) for idx,s in enumerate(["Detected","Analyzed","Contained","Resolved"])], recommended_response=a["response"])
        service.save_incident(db, item, payload.alert_id)
        return item


@router.patch("/incidents/{incident_id}/status")
def status(incident_id: str, payload: IncidentStatusUpdate):
    return service.update_incident(incident_id, payload.status)