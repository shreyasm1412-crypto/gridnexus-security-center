# GridNexus AI — Backend Architecture & Quick Start Guide

Smart grid cybersecurity simulation and AI threat detection backend built with **Python**, **FastAPI**, **scikit-learn**, and **Pydantic**.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ installed

### 2. Set Up Python Virtual Environment

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI Server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend server is now live at:
- **API Base:** `http://localhost:8000/api`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### 5. Run the Test Suite

```bash
python test_backend.py
```

---

## ⚡ Architecture & Flow

```
+-------------------------------------------------------------------------------+
|                        SMART GRID DIGITAL TWIN                                |
|  - 10 Assets: Power Source, Main Substation, Feeders A/B, Smart Meters 01-06  |
|  - Live electrical telemetry (V, I, f, P) + Network telemetry (latency, loss) |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                    HYBRID THREAT DETECTION PIPELINE                           |
|  1. Rule Engine: Physical electrical tolerances + network flood thresholds    |
|  2. Isolation Forest (sklearn): Unsupervised anomaly detection on baseline    |
|  3. Random Forest (sklearn): Supervised 4-class cyberattack classifier        |
|  ==> Hybrid Decision Fusion: Combined evidence, confidence, and explanation   |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       RISK & SEVERITY ENGINE (0-100)                          |
|  Deterministic scoring: Confidence + Anomaly + Rules + Asset Criticality      |
|  Severity: LOW (0-24) | MEDIUM (25-49) | HIGH (50-74) | CRITICAL (75-100)     |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                          SOC INCIDENT MANAGEMENT                              |
|  - Automated Alert creation (/api/alerts)                                     |
|  - Automated Incident lifecycle tracking (/api/incidents)                     |
|    OPEN -> INVESTIGATING -> CONTAINED -> RESOLVED                             |
|  - Safe Simulated Mitigation Recommendations                                  |
+-------------------------------------------------------------------------------+
```

---

## 📡 API Endpoints Reference

### Health
- `GET /api/health` — Service health and model status

### Command Center / Dashboard
- `GET /api/dashboard` — Live grid health, active threats, risk score, 24h performance curve

### Smart Grid Digital Twin
- `GET /api/grid/live-data` — Raw telemetry for all 10 devices
- `GET /api/grid/devices` — Formatted device nodes with engineering units
- `GET /api/grid/devices/{device_id}` — Individual node inspection
- `GET /api/grid/topology` — Digital twin topology nodes & transmission edges

### Attack Simulation
- `POST /api/simulation/normal` — Reset grid to normal operation
- `POST /api/simulation/fdi` — False Data Injection targeting SM-04
- `POST /api/simulation/dos` — Denial of Service targeting Feeder B (FDR-B)
- `POST /api/simulation/unauthorized-access` — Unauthorized Access targeting SUB-01
- `GET /api/simulation/status` — Active simulation scenario & stage

### Alerts
- `GET /api/alerts` — Active and historical alerts with detection evidence
- `GET /api/alerts/{alert_id}` — Alert detail & recommended response

### Incidents
- `GET /api/incidents` — Incident list and current lifecycle status
- `GET /api/incidents/{incident_id}` — Incident detail with stage timeline
- `PATCH /api/incidents/{incident_id}/status` — Transition status (`Open`, `Investigating`, `Contained`, `Resolved`)
