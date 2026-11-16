"""Transactional simulation workflow using existing sklearn inference engines."""
import json
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from ..database import connection, migrate
from ..state import twin, hybrid_engine, risk_engine, anomaly_detector, attack_classifier
from .alert_service import AlertService
from .incident_service import IncidentService
from .response_engine import SimulatedResponseEngine


def now():
    return datetime.now(timezone.utc).isoformat()


def severity(score):
    return "LOW" if score <= 25 else "MEDIUM" if score <= 50 else "HIGH" if score <= 75 else "CRITICAL"


def baseline(device_id):
    s = twin.device_specs[device_id]
    return dict(device_id=device_id, device_name=s["name"], device_type=s["type"], status="normal",
                voltage=s["nominal_v"], current=s["nominal_i"], frequency=s["nominal_f"], power=s["nominal_p"],
                network_latency=s["base_latency"], packet_rate=s["base_packet_rate"], packet_loss=s["base_loss"],
                failed_login_attempts=0, timestamp=now())


def save_telemetry(db, t, simulation_id=None):
    db.execute("INSERT INTO telemetry(device_id,voltage,current,frequency,power,network_latency,packet_rate,packet_loss,failed_login_attempts,timestamp,simulation_id) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
               tuple(t[k] for k in ("device_id", "voltage", "current", "frequency", "power", "network_latency", "packet_rate", "packet_loss", "failed_login_attempts", "timestamp")) + (simulation_id,))


def save_alert(db, a, timestamp, simulation_id=None):
    a["severity"] = severity(a["risk"])
    db.execute("INSERT INTO alerts VALUES(?,?,?,?,?,?,?,?,?,?,?)", (a["id"], a["device"], a["type"], a["method"], a["confidence"], a["risk"], a["severity"], a["status"], timestamp, json.dumps(a), simulation_id))


def save_incident(db, i, alert_id):
    i["severity"] = severity(i["risk"])
    i["alert_id"] = alert_id
    db.execute("INSERT INTO incidents VALUES(?,?,?,?,?,?,?,?,?)", (i["id"], alert_id, i["type"], i["device"], i["severity"], i["risk"], i["status"], i["time"], json.dumps(i)))


def initialize():
    with connection() as db:
        migrate(db)
        if db.execute("SELECT COUNT(*) FROM devices").fetchone()[0]:
            return
        for device_id, spec in twin.device_specs.items():
            db.execute("INSERT INTO devices VALUES(?,?,?,?)", (device_id, spec["name"], spec["type"], "normal"))
            save_telemetry(db, baseline(device_id))
        seed_alerts = [a.model_dump() for a in AlertService().get_all()]
        for a in seed_alerts:
            a.update(triggered_rules=a["evidence"][:2], anomaly_score=0.61, classification_confidence=a["confidence"])
            save_alert(db, a, "2026-11-02T" + a["time"] + "+00:00")
        for i in IncidentService().get_all():
            item = i.model_dump()
            match = next((a for a in seed_alerts if a["device"] == i.device and a["type"] == i.type), None)
            if match is None:
                match = dict(id="ALT-SEED-" + i.id, device=i.device, type=i.type, method="Hybrid Detection", confidence=80,
                             risk=i.risk, severity=severity(i.risk), status=i.status, time=i.time[-5:] + ":00",
                             summary="Historical simulated incident.", evidence=[], response=item["recommended_response"],
                             triggered_rules=[], anomaly_score=0.0, classification_confidence=80)
                save_alert(db, match, i.time)
            save_incident(db, item, match["id"])


def telemetry_rows(db):
    return [dict(r) for r in db.execute("SELECT t.*,d.name AS device_name,d.type AS device_type,d.status FROM telemetry t JOIN devices d ON d.id=t.device_id WHERE t.id=(SELECT MAX(id) FROM telemetry WHERE device_id=t.device_id) ORDER BY d.rowid")]


def all_payloads(db, table):
    return [json.loads(r[0]) for r in db.execute(f"SELECT payload FROM {table} ORDER BY rowid DESC")]


def run(attack, device_id, request_id=None):
    from ..models.schemas import DeviceTelemetry
    if device_id not in twin.device_specs:
        raise HTTPException(422, "Unknown target device")
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        if request_id:
            previous = db.execute("SELECT result,attack_type,target_device FROM simulation_history WHERE request_id=?", (request_id,)).fetchone()
            if previous:
                if previous[1] != attack or previous[2] != device_id:
                    raise HTTPException(409, "Request ID was already used for another simulation")
                return json.loads(previous[0])
        stamp, simulation_id = now(), "SIM-" + uuid4().hex[:12]
        values = baseline(device_id)
        if attack == "fdi":
            values.update(voltage=values["voltage"] * 1.248, current=values["current"] * 2.93,
                          power=values["power"] * 3.7, frequency=50.48, network_latency=48, status="threat")
        elif attack == "dos":
            values.update(network_latency=286, packet_rate=3420, packet_loss=28.5, status="threat")
        elif attack == "ua":
            values.update(failed_login_attempts=16, packet_rate=680, network_latency=21, status="threat")
        telem = DeviceTelemetry(**values)
        detection = hybrid_engine.evaluate(telem, twin.device_specs[device_id])
        risk = risk_engine.calculate_risk(telem, detection, twin.device_specs[device_id]["nominal_v"])
        health = {"normal": 96, "fdi": 72, "dos": 81, "ua": 89}[attack]
        a = i = None
        if attack != "normal" and detection.suspicious and detection.final_threat_type != "Normal":
            a = dict(id="ALT-" + uuid4().hex[:12], time=stamp[11:19], device=device_id, type=detection.final_threat_type,
                     method="Hybrid Detection", confidence=round(detection.final_confidence), risk=risk.risk_score,
                     severity=severity(risk.risk_score), status="Open", summary=detection.summary,
                     evidence=detection.evidence, response=SimulatedResponseEngine.get_recommended_response(detection.final_threat_type),
                     triggered_rules=detection.triggered_rules, anomaly_score=detection.anomaly_score,
                     classification_confidence=detection.class_probabilities.get(detection.final_threat_type, 0))
            if detection.final_threat_type != "Unknown Anomaly":
                i = dict(id="INC-" + uuid4().hex[:12], type=a["type"], device=device_id, severity=a["severity"],
                         time=stamp[:16].replace("T", " "), risk=a["risk"], status="Open", alert_id=a["id"],
                         timeline=[dict(stage=stage, time=stamp if idx == 0 else "--", completed=idx == 0) for idx, stage in enumerate(["Detected", "Analyzed", "Contained", "Resolved"])],
                         recommended_response=a["response"])
        response = dict(mode=attack, target=device_id if attack != "normal" else None, grid_health=health,
                        latency=round(telem.network_latency), confidence=round(detection.final_confidence), risk=risk.risk_score,
                        detection=detection.model_dump(), risk_assessment=risk.model_dump(), active_alert=a, active_incident=i,
                        telemetry=telem.model_dump(), simulation_id=simulation_id,
                        title={"normal": "Normal Operation", "fdi": "False Data Injection", "dos": "Denial of Service", "ua": "Unauthorized Access"}[attack],
                        description="Software-only simulated grid", stage=0 if attack == "normal" else 4, message="Simulation processed")
        db.execute("UPDATE simulation_history SET status='Completed',end_time=? WHERE status='Active'", (stamp,))
        db.execute("INSERT INTO simulation_history VALUES(?,?,?,?,?,?,?,?)", (simulation_id, device_id, attack, "Completed" if attack == "normal" else "Active", stamp, stamp if attack == "normal" else None, json.dumps(response), request_id))
        db.execute("UPDATE devices SET status='normal'")
        for id_ in twin.device_specs:
            t = values if id_ == device_id else baseline(id_)
            save_telemetry(db, t, simulation_id)
            db.execute("UPDATE devices SET status=? WHERE id=?", (t["status"], id_))
        if a:
            save_alert(db, a, stamp, simulation_id)
        if i:
            save_incident(db, i, a["id"])
        return response


def update_incident(id_, status):
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT payload,alert_id FROM incidents WHERE id=?", (id_,)).fetchone()
        if not row:
            raise HTTPException(404, "Incident not found")
        item = json.loads(row[0])
        item["status"] = status
        idx = ["Open", "Investigating", "Contained", "Resolved"].index(status)
        for n, event in enumerate(item["timeline"]):
            event.update(completed=n <= idx, time=(now() if event["time"] == "--" else event["time"]) if n <= idx else "--")
        db.execute("UPDATE incidents SET status=?,payload=? WHERE id=?", (status, json.dumps(item), id_))
        alert = json.loads(db.execute("SELECT payload FROM alerts WHERE id=?", (row[1],)).fetchone()[0])
        alert["status"] = status
        db.execute("UPDATE alerts SET status=?,payload=? WHERE id=?", (status, json.dumps(alert), row[1]))
        return item


def snapshot():
    with connection() as db:
        db.execute("BEGIN")
        rows = telemetry_rows(db)
        alerts, incidents = all_payloads(db, "alerts"), all_payloads(db, "incidents")
        active = db.execute("SELECT result FROM simulation_history WHERE status='Active'").fetchone()
        latest = db.execute("SELECT result FROM simulation_history ORDER BY rowid DESC LIMIT 1").fetchone()
        result = json.loads((active or latest)[0]) if active or latest else None
        if result and result["active_alert"]:
            result["active_alert"] = next((a for a in alerts if a["id"] == result["active_alert"]["id"]), result["active_alert"])
        normal_count = db.execute("SELECT COUNT(*) FROM telemetry WHERE simulation_id IS NULL OR simulation_id IN (SELECT id FROM simulation_history WHERE attack_type='normal')").fetchone()[0]
        active_alerts = [a for a in alerts if a["status"] in ("Open", "Investigating")]
        return dict(telemetry=rows, alerts=alerts, incidents=incidents, simulation=result,
                    dashboard=dict(grid_health=result["grid_health"] if result else 96, connected_devices=len(rows),
                                   active_threats=len(active_alerts), overall_risk=max((a["risk"] for a in active_alerts), default=12),
                                   security_status="Threat Detected" if active_alerts else "Secure",
                                   security_overview=dict(normal=normal_count, suspicious=len(alerts), critical=sum(a["severity"] == "CRITICAL" for a in active_alerts)),
                                   total_events=normal_count + len(alerts)),
                    models_loaded=bool(anomaly_detector.is_trained and attack_classifier.is_trained))