from __future__ import annotations
from radio_core import AircraftState

try:
    from SimConnect import SimConnect, AircraftRequests
except Exception:
    SimConnect = None
    AircraftRequests = None


class MSFSSimBridge:
    """Bridge to MSFS 2020 and 2024 via SimConnect.
    Falls back to a rotating demo state if SimConnect is unavailable.
    """

    def __init__(self):
        self.sm = None
        self.aq = None
        self._fallback_index = 0
        self.available = False

    def connect(self) -> bool:
        if SimConnect is None or AircraftRequests is None:
            self.available = False
            return False
        try:
            self.sm = SimConnect()
            self.aq = AircraftRequests(self.sm, _time=200)
            self.available = True
            return True
        except Exception:
            self.available = False
            return False

    def disconnect(self):
        self.sm = None
        self.aq = None
        self.available = False

    def _fallback_state(self, callsign: str, ptt_pressed: bool) -> AircraftState:
        samples = [
            (51.4706, -0.4619, 4500, 270, 190, 119.730, 121.500),
            (51.3000, -0.2800, 3800, 250, 175, 118.005, 121.500),
            (51.1537, -0.1821, 2200, 180, 160, 118.005, 121.500),
        ]
        s = samples[self._fallback_index % len(samples)]
        self._fallback_index += 1
        return AircraftState(
            callsign=callsign,
            lat=s[0], lon=s[1], alt_ft=s[2], heading_deg=s[3],
            groundspeed_kts=s[4], com1_active_mhz=s[5], com1_standby_mhz=s[6],
            ptt_pressed=ptt_pressed,
        )

    def to_aircraft_state(self, callsign: str, ptt_pressed: bool) -> AircraftState:
        if not self.available or self.aq is None:
            return self._fallback_state(callsign, ptt_pressed)
        try:
            lat = float(self.aq.get('PLANE LATITUDE'))
            lon = float(self.aq.get('PLANE LONGITUDE'))
            alt_ft = float(self.aq.get('PLANE ALTITUDE'))
            heading_deg = float(self.aq.get('PLANE HEADING DEGREES TRUE'))
            groundspeed_kts = float(self.aq.get('GROUND VELOCITY')) * 1.94384
            com1_active_hz = float(self.aq.get('COM ACTIVE FREQUENCY:1'))
            com1_standby_hz = float(self.aq.get('COM STANDBY FREQUENCY:1'))
            return AircraftState(
                callsign=callsign,
                lat=lat, lon=lon, alt_ft=alt_ft,
                heading_deg=heading_deg, groundspeed_kts=groundspeed_kts,
                com1_active_mhz=round(com1_active_hz / 1_000_000.0, 3),
                com1_standby_mhz=round(com1_standby_hz / 1_000_000.0, 3),
                ptt_pressed=ptt_pressed,
            )
        except Exception:
            return self._fallback_state(callsign, ptt_pressed)
