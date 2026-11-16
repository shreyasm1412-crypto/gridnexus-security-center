"""SQLite connections and schema. Durable state never depends on process memory."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def connection():
    path = Path(os.environ.get("GRIDNEXUS_DB_PATH", "/tmp/gridnexus/gridnexus.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    try:
        with db:
            yield db
    finally:
        db.close()


def migrate(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS devices (
      id TEXT PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('normal','warning','threat','offline'))
    );
    CREATE TABLE IF NOT EXISTS simulation_history (
      id TEXT PRIMARY KEY, target_device TEXT NOT NULL REFERENCES devices(id),
      attack_type TEXT NOT NULL CHECK(attack_type IN ('normal','fdi','dos','ua')),
      status TEXT NOT NULL CHECK(status IN ('Active','Completed')),
      start_time TEXT NOT NULL, end_time TEXT, result TEXT NOT NULL, request_id TEXT UNIQUE
    );
    CREATE UNIQUE INDEX IF NOT EXISTS one_active_simulation ON simulation_history(status) WHERE status='Active';
    CREATE TABLE IF NOT EXISTS telemetry (
      id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT NOT NULL REFERENCES devices(id),
      voltage REAL NOT NULL, current REAL NOT NULL, frequency REAL NOT NULL,
      power REAL NOT NULL, network_latency REAL NOT NULL, packet_rate REAL NOT NULL,
      packet_loss REAL NOT NULL, failed_login_attempts INTEGER NOT NULL,
      timestamp TEXT NOT NULL, simulation_id TEXT REFERENCES simulation_history(id)
    );
    CREATE INDEX IF NOT EXISTS telemetry_device ON telemetry(device_id,id DESC);
    CREATE TABLE IF NOT EXISTS alerts (
      id TEXT PRIMARY KEY, device_id TEXT NOT NULL REFERENCES devices(id), threat_type TEXT NOT NULL,
      detection_method TEXT NOT NULL, confidence INTEGER NOT NULL CHECK(confidence BETWEEN 0 AND 100),
      risk_score INTEGER NOT NULL CHECK(risk_score BETWEEN 0 AND 100), severity TEXT NOT NULL,
      status TEXT NOT NULL, timestamp TEXT NOT NULL, payload TEXT NOT NULL,
      simulation_id TEXT UNIQUE REFERENCES simulation_history(id)
    );
    CREATE TABLE IF NOT EXISTS incidents (
      id TEXT PRIMARY KEY, alert_id TEXT NOT NULL UNIQUE REFERENCES alerts(id),
      threat_type TEXT NOT NULL, device_id TEXT NOT NULL REFERENCES devices(id),
      severity TEXT NOT NULL, risk_score INTEGER NOT NULL CHECK(risk_score BETWEEN 0 AND 100),
      status TEXT NOT NULL CHECK(status IN ('Open','Investigating','Contained','Resolved')),
      detection_time TEXT NOT NULL, payload TEXT NOT NULL
    );
    PRAGMA user_version=1;
    """)