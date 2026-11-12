import math
import time
from datetime import datetime
from typing import List
from fastapi import APIRouter
from ..models.schemas import (
    DashboardResponse,
    SecurityOverview,
    RecentEvent,
    SystemStatusItem,
    GridPerformancePoint,
)
from ..state import twin, attack_simulator, alert_service, hybrid_engine, risk_engine

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    scenario = attack_simulator.get_current_scenario()
    mode = attack_simulator.active_mode
    is_normal = mode == "normal"

    grid_health = scenario["grid_health"]
    connected_devices = 24

    if is_normal or not scenario.get("target"):
        overall_risk = 12
        active_threats = 0
    else:
        target_id = scenario["target"]
        telem = twin.get_device_telemetry(target_id)
        nominals = twin.device_specs[target_id]
        detection = hybrid_engine.evaluate(telem, nominals)
        risk_res = risk_engine.calculate_risk(telem, detection, nominals.get("nominal_v", 230.0))
        overall_risk = risk_res.risk_score
        active_threats = 1 if detection.suspicious else 0

    security_status = "Secure" if is_normal else "Threat Detected"

    # Security event counts
    if is_normal:
        sec_overview = SecurityOverview(normal=1248, suspicious=3, critical=0)
    elif mode == "fdi":
        sec_overview = SecurityOverview(normal=1239, suspicious=8, critical=4)
    elif mode == "dos":
        sec_overview = SecurityOverview(normal=1214, suspicious=27, critical=10)
    else:  # ua
        sec_overview = SecurityOverview(normal=1240, suspicious=9, critical=2)

    # Dynamic 24-point performance curve
    t_sec = time.time()
    perf: List[GridPerformancePoint] = []
    for i in range(24):
        h = f"{i:02d}:00"
        # Base sinusoidal wave
        v = 230.0 + math.sin(i / 3.0) * 2.4 + ((i * 7) % 5) * 0.2
        f = 50.0 + math.sin(i / 2.0) * 0.04
        load = round(140 + math.sin((i - 6) / 3.8) * 45 + ((i * 13) % 7))

        # Show disturbance in the latest hours if under attack
        if not is_normal and i >= 20:
            if mode == "fdi":
                v += 18.5
                f += 0.25
            elif mode == "dos":
                load += 22
            elif mode == "ua":
                f -= 0.12

        perf.append(GridPerformancePoint(
            time=h,
            voltage=round(v, 1),
            frequency=round(f, 2),
            load=float(load),
        ))

    # Recent security events
    now_str = datetime.now().strftime("%H:%M:%S")
    recent_events = [
        RecentEvent(id=1, text="Security monitoring cycle completed", time=now_str),
        RecentEvent(
            id=2,
            text=f"Telemetry scan: {scenario['title']} active" if not is_normal else "Smart Meter SM-04 telemetry verified",
            time=now_str,
        ),
        RecentEvent(id=3, text="Main Substation connection stable", time=now_str),
        RecentEvent(id=4, text="Feeder A data integrity verified", time=now_str),
        RecentEvent(id=5, text="Hybrid Detection baseline refreshed", time=now_str),
    ]

    # Grid status labels
    grid_status = ["Main Substation", "Feeder A", "Feeder B", "Smart Meter Cluster"]

    # System status modal items
    system_status = [
        SystemStatusItem(label="System", value="Online", status="normal"),
        SystemStatusItem(label="Simulation", value=scenario["title"], status="normal" if is_normal else "threat"),
        SystemStatusItem(label="Connected Devices", value=str(connected_devices), status="normal"),
        SystemStatusItem(
            label="Security Status",
            value=security_status,
            status="normal" if is_normal else "threat",
        ),
    ]

    return DashboardResponse(
        grid_health=grid_health,
        security_status=security_status,
        connected_devices=connected_devices,
        active_threats=active_threats,
        overall_risk=overall_risk,
        system_status=system_status,
        security_overview=sec_overview,
        recent_events=recent_events,
        grid_status=grid_status,
        grid_performance=perf,
        active_attack=mode,
        active_target=scenario.get("target"),
    )
