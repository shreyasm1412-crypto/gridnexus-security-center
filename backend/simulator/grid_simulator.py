import math
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
from ..models.schemas import DeviceTelemetry, GridNodeSchema, DeviceStatus

class SmartGridDigitalTwin:
    """
    Simulated Smart Grid Digital Twin representing:
    - 1 Power Source (PS-01)
    - 1 Main Substation (SUB-01)
    - 2 Feeders (FDR-A, FDR-B)
    - 6 Smart Meters (SM-01 to SM-06)
    """

    def __init__(self):
        # Base specifications for the 10 smart grid nodes
        self.device_specs = {
            "PS-01": {
                "name": "Power Source",
                "type": "Power Source",
                "nominal_v": 132000.0,  # 132 kV
                "nominal_i": 1210.0,    # A
                "nominal_f": 50.00,     # Hz
                "nominal_p": 160000.0,  # 160 MW (in kW: 160,000 kW)
                "base_latency": 6.0,
                "base_packet_rate": 450.0,
                "base_loss": 0.05,
                "display_unit_v": "kV",
                "display_unit_p": "MW",
            },
            "SUB-01": {
                "name": "Main Substation",
                "type": "Substation",
                "nominal_v": 33000.0,   # 33 kV
                "nominal_i": 2840.0,    # A
                "nominal_f": 50.01,
                "nominal_p": 158000.0,  # 158 MW
                "base_latency": 9.0,
                "base_packet_rate": 380.0,
                "base_loss": 0.08,
                "display_unit_v": "kV",
                "display_unit_p": "MW",
            },
            "FDR-A": {
                "name": "Feeder A",
                "type": "Feeder",
                "nominal_v": 11000.0,   # 11 kV
                "nominal_i": 4120.0,    # A
                "nominal_f": 50.00,
                "nominal_p": 78000.0,   # 78 MW
                "base_latency": 12.0,
                "base_packet_rate": 260.0,
                "base_loss": 0.12,
                "display_unit_v": "kV",
                "display_unit_p": "MW",
            },
            "FDR-B": {
                "name": "Feeder B",
                "type": "Feeder",
                "nominal_v": 11000.0,   # 11 kV
                "nominal_i": 4050.0,    # A
                "nominal_f": 49.99,
                "nominal_p": 77000.0,   # 77 MW
                "base_latency": 13.0,
                "base_packet_rate": 255.0,
                "base_loss": 0.10,
                "display_unit_v": "kV",
                "display_unit_p": "MW",
            },
            # 6 Smart Meters connected to Feeders (SM-01 to SM-03 on FDR-A, SM-04 to SM-06 on FDR-B)
            "SM-01": {"name": "Smart Meter 01", "type": "Smart Meter", "nominal_v": 230.0, "nominal_i": 18.0, "nominal_f": 50.00, "nominal_p": 4.1, "base_latency": 18.0, "base_packet_rate": 62.0, "base_loss": 0.15, "display_unit_v": "V", "display_unit_p": "kW"},
            "SM-02": {"name": "Smart Meter 02", "type": "Smart Meter", "nominal_v": 230.4, "nominal_i": 19.3, "nominal_f": 50.00, "nominal_p": 4.4, "base_latency": 20.0, "base_packet_rate": 60.0, "base_loss": 0.18, "display_unit_v": "V", "display_unit_p": "kW"},
            "SM-03": {"name": "Smart Meter 03", "type": "Smart Meter", "nominal_v": 230.8, "nominal_i": 20.6, "nominal_f": 50.00, "nominal_p": 4.7, "base_latency": 22.0, "base_packet_rate": 64.0, "base_loss": 0.14, "display_unit_v": "V", "display_unit_p": "kW"},
            "SM-04": {"name": "Smart Meter 04", "type": "Smart Meter", "nominal_v": 231.2, "nominal_i": 21.9, "nominal_f": 50.00, "nominal_p": 5.0, "base_latency": 24.0, "base_packet_rate": 58.0, "base_loss": 0.20, "display_unit_v": "V", "display_unit_p": "kW"},
            "SM-05": {"name": "Smart Meter 05", "type": "Smart Meter", "nominal_v": 231.6, "nominal_i": 23.2, "nominal_f": 50.00, "nominal_p": 5.3, "base_latency": 26.0, "base_packet_rate": 61.0, "base_loss": 0.16, "display_unit_v": "V", "display_unit_p": "kW"},
            "SM-06": {"name": "Smart Meter 06", "type": "Smart Meter", "nominal_v": 232.0, "nominal_i": 24.5, "nominal_f": 50.00, "nominal_p": 5.6, "base_latency": 28.0, "base_packet_rate": 59.0, "base_loss": 0.22, "display_unit_v": "V", "display_unit_p": "kW"},
        }

        # Parent hierarchy
        self.parents = {
            "PS-01": None,
            "SUB-01": "PS-01",
            "FDR-A": "SUB-01",
            "FDR-B": "SUB-01",
            "SM-01": "FDR-A",
            "SM-02": "FDR-A",
            "SM-03": "FDR-A",
            "SM-04": "FDR-B",
            "SM-05": "FDR-B",
            "SM-06": "FDR-B",
        }

        # Current live state overrides (e.g. during an attack)
        self.attack_mode: str = "normal"
        self.attack_target: Optional[str] = None
        self.attack_overrides: Dict[str, Dict] = {}

        # Last updated time
        self.start_time = time.time()

    def get_device_telemetry(self, device_id: str) -> DeviceTelemetry:
        """
        Generate live telemetry for a single device, combining
        nominal baseline + dynamic micro-fluctuations + active attack overrides.
        """
        if device_id not in self.device_specs:
            raise ValueError(f"Unknown device: {device_id}")

        spec = self.device_specs[device_id]
        t = time.time() - self.start_time

        # Controlled natural micro-fluctuations (sinusoidal + subtle noise)
        v_offset = math.sin(t / 4.0 + hash(device_id) % 10) * (0.006 * spec["nominal_v"]) + random.uniform(-0.002, 0.002) * spec["nominal_v"]
        f_offset = math.sin(t / 3.0 + hash(device_id) % 7) * 0.015 + random.uniform(-0.008, 0.008)
        i_offset = math.sin(t / 5.0) * (0.01 * spec["nominal_i"]) + random.uniform(-0.005, 0.005) * spec["nominal_i"]
        p_offset = math.sin(t / 5.0) * (0.01 * spec["nominal_p"]) + random.uniform(-0.005, 0.005) * spec["nominal_p"]
        lat_offset = math.sin(t / 2.0) * 1.5 + random.uniform(-0.8, 0.8)
        pkt_offset = random.uniform(-3.0, 3.0)
        loss_offset = random.uniform(-0.02, 0.02)

        voltage = round(spec["nominal_v"] + v_offset, 2)
        frequency = round(spec["nominal_f"] + f_offset, 2)
        current = round(spec["nominal_i"] + i_offset, 2)
        power = round(spec["nominal_p"] + p_offset, 2)
        latency = max(2.0, round(spec["base_latency"] + lat_offset, 1))
        packet_rate = max(10.0, round(spec["base_packet_rate"] + pkt_offset, 1))
        packet_loss = max(0.0, round(spec["base_loss"] + loss_offset, 2))
        failed_logins = 0
        status: DeviceStatus = "normal"

        # Apply attack overrides if device is directly targeted or cascaded
        if device_id in self.attack_overrides:
            ov = self.attack_overrides[device_id]
            if "voltage" in ov:
                voltage = ov["voltage"]
            if "current" in ov:
                current = ov["current"]
            if "frequency" in ov:
                frequency = ov["frequency"]
            if "power" in ov:
                power = ov["power"]
            if "network_latency" in ov:
                latency = ov["network_latency"]
            if "packet_rate" in ov:
                packet_rate = ov["packet_rate"]
            if "packet_loss" in ov:
                packet_loss = ov["packet_loss"]
            if "failed_login_attempts" in ov:
                failed_logins = ov["failed_login_attempts"]
            if "status" in ov:
                status = ov["status"]

        # Timestamp in HH:MM:SS format
        now_str = datetime.now().strftime("%H:%M:%S")

        return DeviceTelemetry(
            device_id=device_id,
            device_name=spec["name"],
            device_type=spec["type"],
            status=status,
            voltage=voltage,
            current=current,
            frequency=frequency,
            power=power,
            network_latency=latency,
            packet_rate=packet_rate,
            packet_loss=packet_loss,
            failed_login_attempts=failed_logins,
            timestamp=now_str,
        )

    def get_all_telemetry(self) -> List[DeviceTelemetry]:
        """Return live telemetry for all 10 smart grid devices."""
        return [self.get_device_telemetry(dev_id) for dev_id in self.device_specs]

    def get_grid_nodes(self) -> List[GridNodeSchema]:
        """
        Format all 10 devices into GridNodeSchema matching the frontend topology view.
        """
        nodes: List[GridNodeSchema] = []
        for dev_id, spec in self.device_specs.items():
            telem = self.get_device_telemetry(dev_id)

            # Format human-readable strings with engineering units
            if spec["display_unit_v"] == "kV":
                v_str = f"{(telem.voltage / 1000.0):.1f} kV" if telem.voltage >= 1000 else f"{telem.voltage:.1f} V"
            else:
                v_str = f"{telem.voltage:.1f} V"

            if spec["display_unit_p"] == "MW":
                p_str = f"{(telem.power / 1000.0):.1f} MW" if telem.power >= 1000 else f"{telem.power:.1f} kW"
            else:
                p_str = f"{telem.power:.1f} kW"

            curr_str = f"{telem.current:,.1f} A" if telem.current >= 100 else f"{telem.current:.1f} A"
            freq_str = f"{telem.frequency:.2f} Hz"

            # Node risk calculation
            if telem.status == "threat":
                node_risk = 88 if dev_id == "SM-04" else 76 if dev_id == "FDR-B" else 84
            elif telem.status == "warning":
                node_risk = 48
            else:
                # Normal baseline risk (low 4 - 12)
                base_risk = 4 if spec["type"] == "Power Source" else 8 if spec["type"] == "Substation" else 10 if spec["type"] == "Feeder" else 6
                node_risk = base_risk

            nodes.append(
                GridNodeSchema(
                    id=dev_id,
                    label=spec["name"],
                    type=spec["type"],
                    voltage=v_str,
                    current=curr_str,
                    frequency=freq_str,
                    power=p_str,
                    latency=int(telem.network_latency),
                    risk=node_risk,
                    status=telem.status,
                    telemetry=telem,
                )
            )
        return nodes

    def set_attack_mode(self, mode: str, target: Optional[str], overrides: Dict[str, Dict]):
        """Update active attack mode and device overrides."""
        self.attack_mode = mode
        self.attack_target = target
        self.attack_overrides = overrides

    def reset_to_normal(self):
        """Reset digital twin to pure normal operation."""
        self.attack_mode = "normal"
        self.attack_target = None
        self.attack_overrides = {}
