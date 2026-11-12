"""
Automated unit & integration test runner for GridNexus AI backend.
Can be executed with pytest or directly with `python test_backend.py`.
"""
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    print("Testing /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "healthy"
    print("  -> Health OK")

def test_grid_devices_and_topology():
    print("Testing /api/grid endpoints...")
    res = client.get("/api/grid/live-data")
    assert res.status_code == 200
    devices = res.json()
    assert len(devices) == 10, f"Expected 10 devices, got {len(devices)}"

    # Check nominals on devices
    dev_ids = [d["device_id"] for d in devices]
    assert "PS-01" in dev_ids
    assert "SUB-01" in dev_ids
    assert "FDR-A" in dev_ids
    assert "FDR-B" in dev_ids
    assert "SM-04" in dev_ids

    res_topo = client.get("/api/grid/topology")
    assert res_topo.status_code == 200
    topo = res_topo.json()
    assert len(topo["nodes"]) == 10
    assert len(topo["edges"]) == 9
    print("  -> Grid devices & topology OK (10 nodes, 9 edges)")

def test_dashboard():
    print("Testing /api/dashboard...")
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    dash = res.json()
    assert "grid_health" in dash
    assert "overall_risk" in dash
    assert len(dash["grid_performance"]) == 24
    print("  -> Dashboard OK")

def test_fdi_simulation():
    print("Testing /api/simulation/fdi (False Data Injection)...")
    res = client.post("/api/simulation/fdi")
    assert res.status_code == 200, res.text
    sim = res.json()
    assert sim["mode"] == "fdi"
    assert sim["target"] == "SM-04"
    assert sim["detection"]["final_threat_type"] == "False Data Injection"
    assert sim["detection"]["anomaly_detected"] is True
    assert sim["detection"]["final_confidence"] >= 85
    assert sim["risk_assessment"]["severity"] in ["HIGH", "CRITICAL"]
    assert sim["active_alert"] is not None
    assert sim["active_incident"] is not None
    print(f"  -> FDI simulation OK: Threat={sim['detection']['final_threat_type']}, Confidence={sim['detection']['final_confidence']}%, Risk={sim['risk']}")

def test_dos_simulation():
    print("Testing /api/simulation/dos (Denial of Service)...")
    res = client.post("/api/simulation/dos")
    assert res.status_code == 200, res.text
    sim = res.json()
    assert sim["mode"] == "dos"
    assert sim["target"] == "FDR-B"
    assert sim["detection"]["final_threat_type"] == "Denial of Service"
    assert sim["detection"]["anomaly_detected"] is True
    assert sim["risk_assessment"]["severity"] in ["HIGH", "CRITICAL"]
    print(f"  -> DoS simulation OK: Threat={sim['detection']['final_threat_type']}, Confidence={sim['detection']['final_confidence']}%, Risk={sim['risk']}")

def test_unauthorized_access_simulation():
    print("Testing /api/simulation/unauthorized-access (Unauthorized Access)...")
    res = client.post("/api/simulation/unauthorized-access")
    assert res.status_code == 200, res.text
    sim = res.json()
    assert sim["mode"] == "ua"
    assert sim["target"] == "SUB-01"
    assert sim["detection"]["final_threat_type"] == "Unauthorized Access"
    print(f"  -> UA simulation OK: Threat={sim['detection']['final_threat_type']}, Confidence={sim['detection']['final_confidence']}%, Risk={sim['risk']}")

def test_normal_reset():
    print("Testing /api/simulation/normal (Reset)...")
    res = client.post("/api/simulation/normal")
    assert res.status_code == 200, res.text
    sim = res.json()
    assert sim["mode"] == "normal"
    assert sim["detection"]["final_threat_type"] == "Normal"
    print("  -> Reset to normal OK")

def test_alerts_and_incidents():
    print("Testing /api/alerts and /api/incidents...")
    # Trigger an attack to ensure fresh alert and incident
    client.post("/api/simulation/fdi")

    res_alerts = client.get("/api/alerts")
    assert res_alerts.status_code == 200
    alerts = res_alerts.json()
    assert len(alerts) > 0
    top_alert = alerts[0]
    alert_id = top_alert["id"]

    res_single_alert = client.get(f"/api/alerts/{alert_id}")
    assert res_single_alert.status_code == 200
    assert res_single_alert.json()["id"] == alert_id

    # Check incidents
    res_inc = client.get("/api/incidents")
    assert res_inc.status_code == 200
    incs = res_inc.json()
    assert len(incs) > 0
    inc_id = incs[0]["id"]

    # Patch incident status
    res_patch = client.patch(f"/api/incidents/{inc_id}/status", json={"status": "Contained"})
    assert res_patch.status_code == 200
    patched = res_patch.json()
    assert patched["status"] == "Contained"

    # Verify timeline updated
    contained_stage = next(s for s in patched["timeline"] if s["stage"] == "Contained")
    assert contained_stage["completed"] is True
    print(f"  -> Alerts & Incidents OK (Alert {alert_id}, Incident {inc_id} updated to Contained)")

def run_all():
    print("==================================================")
    print("  GRIDNEXUS AI - BACKEND TEST SUITE")
    print("==================================================")
    test_health()
    test_grid_devices_and_topology()
    test_dashboard()
    test_fdi_simulation()
    test_dos_simulation()
    test_unauthorized_access_simulation()
    test_normal_reset()
    test_alerts_and_incidents()
    print("==================================================")
    print("  ALL BACKEND TESTS PASSED SUCCESSFULLY! (8/8)")
    print("==================================================")

if __name__ == "__main__":
    run_all()
