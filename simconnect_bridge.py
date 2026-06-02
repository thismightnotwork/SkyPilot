from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

try:
    from SimConnect import SimConnect, AircraftRequests
    _SIMCONNECT_AVAILABLE = True
except ImportError:
    _SIMCONNECT_AVAILABLE = False

from radio_core import AircraftState


@dataclass
class SimSnapshot:
    lat: float
    lon: float
    alt_ft: float
    com1_active_mhz: float
    com1_standby_mhz: float
    heading_deg: float
    groundspeed_kts: float
    on_ground: bool


class MSFSSimBridge:
    """
    SimConnect bridge for MSFS 2020 and MSFS 2024.
    Both simulators expose identical SimConnect variable names for the data
    SkyPilot needs, so one bridge class handles both versions.
    """

    def __init__(self) -> None:
        self._sm = None
        self._aq = None

    @property
    def connected(self) -> bool:
        return self._sm is not None

    def connect(self) -> None:
        if not _SIMCONNECT_AVAILABLE:
            raise RuntimeError("SimConnect Python library is not installed. Run: pip install SimConnect")
        self._sm = SimConnect()
        self._aq = AircraftRequests(self._sm, _time=200)

    def disconnect(self) -> None:
        if self._sm:
            self._sm.exit()
            self._sm = None
            self._aq = None

    def snapshot(self) -> SimSnapshot:
        if not self._aq:
            raise RuntimeError("Not connected to simulator")
        aq = self._aq
        lat = float(aq.get("PLANE LATITUDE"))
        lon = float(aq.get("PLANE LONGITUDE"))
        alt_ft = float(aq.get("PLANE ALTITUDE"))
        heading = float(aq.get("PLANE HEADING DEGREES TRUE"))
        gs_kts = float(aq.get("GROUND VELOCITY"))
        on_ground = bool(int(aq.get("SIM ON GROUND") or 0))
        com1_hz = float(aq.get("COM ACTIVE FREQUENCY:1") or 122_800_000)
        com1_stby_hz = float(aq.get("COM STANDBY FREQUENCY:1") or 121_500_000)
        return SimSnapshot(
            lat=lat,
            lon=lon,
            alt_ft=alt_ft,
            com1_active_mhz=round(com1_hz / 1_000_000, 3),
            com1_standby_mhz=round(com1_stby_hz / 1_000_000, 3),
            heading_deg=round(heading, 1),
            groundspeed_kts=round(gs_kts, 1),
            on_ground=on_ground,
        )

    def to_aircraft_state(self, callsign: str, ptt: bool) -> AircraftState:
        s = self.snapshot()
        return AircraftState(
            callsign=callsign,
            lat=s.lat,
            lon=s.lon,
            alt_ft=s.alt_ft,
            com1_active_mhz=s.com1_active_mhz,
            com1_standby_mhz=s.com1_standby_mhz,
            ptt_pressed=ptt,
            radio_powered=True,
        )
