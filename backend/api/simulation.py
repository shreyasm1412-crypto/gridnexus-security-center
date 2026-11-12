from typing import Dict, Any, Optional
from fastapi import APIRouter
from ..models.schemas import SimulationResponse, AttackKey
from ..state import (
    twin,
    attack_simulator,
    hybrid_engine,
    risk_engine,
    alert_service,
    incident_service,
)
from ..services.response_engine import SimulatedResponseEngine

router = APIRouter(prefix="/simulation", tags=["Simulation"])

def _execute_pipeline_and_respond(mode: AttackKey) -> SimulationResponse:
    if mode == "normal":
        scenario = attack_simulator.trigger_normal()
        target_id = "SM-04"  # Sample check
    elif mode == "fdi":
        scenario = attack_simulator.trigger_fdi()
        target_id = "SM-04"
    elif mode == "dos":
        scenario = attack_simulator.trigger_dos()
        target_id = "FDR-B"
    elif mode == "ua":
        scenario = attack_simulator.trigger_unauthorized_access()
        target_id = "SUB-01"
    else:
        raise ValueError(f"Unknown mode: {mode}")

    # 1. Gather telemetry for targeted device
    telem = twin.get_device_telemetry(target_id)
    nominals = twin.device_specs[target_id]

    # 2. Run Hybrid Detection Engine
    detection = hybrid_engine.evaluate(telem, nominals)

    # 3. Calculate Risk & Severity
    risk_res = risk_engine.calculate_risk(telem, detection, nominals.get("nominal_v", 230.0))

    # 4. Create Alert if suspicious
    created_alert = None
    if detection.suspicious and detection.final_threat_type != "Normal":
        responses = SimulatedResponseEngine.get_recommended_response(detection.final_threat_type)
        created_alert = alert_service.create_alert(
            device=target_id,
            threat_type=detection.final_threat_type,
            method="Hybrid Detection",
            confidence=int(detection.final_confidence),
            severity=risk_res.severity,
            risk=risk_res.risk_score,
            summary=detection.summary,
            evidence=detection.evidence,
            response=responses,
            status="Investigating" if risk_res.severity in ["HIGH", "CRITICAL"] else "Open",
        )

    # 5. Create Incident for significant threats (HIGH or CRITICAL)
    created_incident = None
    if detection.suspicious and detection.final_threat_type in ["False Data Injection", "Denial of Service", "Unauthorized Access"]:
        if risk_res.severity in ["HIGH", "CRITICAL"]:
            created_incident = incident_service.create_incident(
                threat_type=detection.final_threat_type,
                device=target_id,
                severity=risk_res.severity,
                risk=risk_res.risk_score,
                status="Investigating",
            )

    msg = (
        f"Simulated {scenario['title']} executed successfully on target {target_id}."
        if mode != "normal"
        else "Simulated smart grid returned to normal operating parameters."
    )

    return SimulationResponse(
        mode=mode,
        title=scenario["title"],
        description=scenario["description"],
        target=scenario.get("target"),
        stage=scenario["stage"],
        grid_health=scenario["grid_health"],
        latency=int(round(telem.network_latency)),
        confidence=int(round(detection.final_confidence)),
        risk=risk_res.risk_score,
        detection=detection,
        risk_assessment=risk_res,
        active_alert=created_alert,
        active_incident=created_incident,
        message=msg,
    )

@router.post("/normal", response_model=SimulationResponse)
def simulate_normal() -> SimulationResponse:
    """Reset grid digital twin to Normal Operation."""
    return _execute_pipeline_and_respond("normal")

@router.post("/fdi", response_model=SimulationResponse)
def simulate_fdi() -> SimulationResponse:
    """Simulate False Data Injection targeting Smart Meter SM-04."""
    return _execute_pipeline_and_respond("fdi")

@router.post("/dos", response_model=SimulationResponse)
def simulate_dos() -> SimulationResponse:
    """Simulate Denial of Service targeting Feeder B (FDR-B)."""
    return _execute_pipeline_and_respond("dos")

@router.post("/unauthorized-access", response_model=SimulationResponse)
def simulate_unauthorized_access() -> SimulationResponse:
    """Simulate Unauthorized Access / Brute-force targeting Main Substation (SUB-01)."""
    return _execute_pipeline_and_respond("ua")

@router.get("/status", response_model=Dict[str, Any])
def get_simulation_status() -> Dict[str, Any]:
    """Get active attack simulation state."""
    sc = attack_simulator.get_current_scenario()
    return {
        "mode": attack_simulator.active_mode,
        "scenario": sc,
    }
