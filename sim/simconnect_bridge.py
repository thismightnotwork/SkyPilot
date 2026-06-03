"""
simconnect_bridge.py — MSFS 2020/2024 SimConnect bridge.
"""
from __future__ import annotations
import threading
import time
from typing import Optional

from .aircraft_state import AircraftState, ComRadio

try:
    from SimConnect import SimConnect, AircraftRequests
    _SC_AVAILABLE = True
except Exception:
    _SC_AVAILABLE = False


def _bcd16_to_mhz(bcd: int) -> float:
    d1 = (bcd >> 12) & 0xF
    d2 = (bcd >>  8) & 0xF
    d3 = (bcd >>  4) & 0xF
    d4 =  bcd        & 0xF
    return 100.0 + d1 * 10 + d2 + d3 * 0.1 + d4 * 0.01


class MSFSSimBridge:
    POLL_HZ = 4

    def __init__(self):
        self._sc        = None
        self._ar        = None
        self._state     = AircraftState()
        self._lock      = threading.Lock()
        self._thread:   Optional[threading.Thread] = None
        self._running   = False
        self._connected = False

    def connect(self) -> bool:
        if not _SC_AVAILABLE:
            self._connected = False
            self._start_demo_thread()
            return False
        try:
            self._sc = SimConnect()
            self._ar = AircraftRequests(self._sc, _time=200)
            self._connected = True
            self._start_poll_thread()
            return True
        except Exception:
            self._connected = False
            self._start_demo_thread()
            return False

    def disconnect(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._sc:
            try:
                self._sc.exit()
            except Exception:
                pass
        self._connected = False

    def get_state(self, callsign: str, ptt_com1: bool = False, ptt_com2: bool = False) -> AircraftState:
        with self._lock:
            s = AircraftState(
                callsign      = callsign,
                lat           = self._state.lat,
                lon           = self._state.lon,
                alt_ft        = self._state.alt_ft,
                heading_deg   = self._state.heading_deg,
                groundspeed_kts = self._state.groundspeed_kts,
                vertical_speed_fpm = self._state.vertical_speed_fpm,
                pitch_deg     = self._state.pitch_deg,
                bank_deg      = self._state.bank_deg,
                squawk        = self._state.squawk,
                on_ground     = self._state.on_ground,
                sim_connected = self._connected,
                ptt_com1      = ptt_com1,
                ptt_com2      = ptt_com2,
                com1 = ComRadio(
                    active_mhz  = self._state.com1.active_mhz,
                    standby_mhz = self._state.com1.standby_mhz,
                ),
                com2 = ComRadio(
                    active_mhz  = self._state.com2.active_mhz,
                    standby_mhz = self._state.com2.standby_mhz,
                ),
            )
        return s

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _start_poll_thread(self):
        self._running = True
        self._thread  = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _start_demo_thread(self):
        self._running = True
        self._thread  = threading.Thread(target=self._demo_loop, daemon=True)
        self._thread.start()

    def _poll_loop(self):
        interval = 1.0 / self.POLL_HZ
        while self._running:
            try:
                ar = self._ar

                def _get(var, default=0.0):
                    try:
                        v = ar.get(var)
                        return float(v) if v is not None else default
                    except Exception:
                        return default

                def _get_freq(var, default=121.800):
                    raw = _get(var, 0)
                    if 100.0 <= raw <= 140.0:
                        return round(raw, 3)
                    try:
                        return _bcd16_to_mhz(int(raw))
                    except Exception:
                        return default

                def _get_squawk(default='2000'):
                    try:
                        raw = ar.get('TRANSPONDER_CODE:1')
                        return str(int(raw)).zfill(4) if raw is not None else default
                    except Exception:
                        return default

                with self._lock:
                    self._state.lat              = _get('PLANE_LATITUDE')
                    self._state.lon              = _get('PLANE_LONGITUDE')
                    self._state.alt_ft           = _get('PLANE_ALTITUDE')
                    self._state.heading_deg      = _get('PLANE_HEADING_DEGREES_TRUE')
                    self._state.groundspeed_kts  = _get('GROUND_VELOCITY')
                    self._state.vertical_speed_fpm = _get('VERTICAL_SPEED')
                    self._state.pitch_deg        = _get('PLANE_PITCH_DEGREES')
                    self._state.bank_deg         = _get('PLANE_BANK_DEGREES')
                    self._state.on_ground        = bool(_get('SIM_ON_GROUND', 1))
                    self._state.squawk           = _get_squawk()
                    self._state.com1.active_mhz  = _get_freq('COM_ACTIVE_FREQUENCY:1', 121.800)
                    self._state.com1.standby_mhz = _get_freq('COM_STANDBY_FREQUENCY:1', 121.500)
                    self._state.com2.active_mhz  = _get_freq('COM_ACTIVE_FREQUENCY:2', 121.500)
                    self._state.com2.standby_mhz = _get_freq('COM_STANDBY_FREQUENCY:2', 118.000)

            except Exception:
                pass

            time.sleep(interval)

    def _demo_loop(self):
        import math
        t = 0.0
        while self._running:
            with self._lock:
                self._state.lat         = 51.1537 + 0.05 * math.sin(t)
                self._state.lon         = -0.1821 + 0.05 * math.cos(t)
                self._state.alt_ft      = 3000.0 + 500.0 * math.sin(t * 0.3)
                self._state.heading_deg = (math.degrees(t) % 360)
                self._state.groundspeed_kts = 180.0
                self._state.on_ground   = False
                self._state.com1.active_mhz  = 118.005
                self._state.com1.standby_mhz = 121.800
                self._state.squawk      = '7000'
            t += 0.05
            time.sleep(0.25)
