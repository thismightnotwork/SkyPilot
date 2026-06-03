"""
aircraft_state.py — Core data models for SkyPilot.

AircraftState mirrors the data swift-project/pilotclient reads from the sim:
  https://github.com/swift-project/pilotclient/blob/main/src/blackmisc/simulation/simulatedaircraft.h

FGCom-mumble compatible radio state is encoded in RadioState.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS_M = 6_371_000.0
NM_TO_M        = 1_852.0
FT_TO_M        = 0.3048


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = radians(lat1), radians(lat2)
    d_phi  = radians(lat2 - lat1)
    d_lam  = radians(lon2 - lon1)
    a = sin(d_phi / 2) ** 2 + cos(p1) * cos(p2) * sin(d_lam / 2) ** 2
    return 2 * EARTH_RADIUS_M * atan2(sqrt(a), sqrt(1 - a))


def radio_horizon_nm(alt_ft: float) -> float:
    return 1.23 * max(0.0, alt_ft) ** 0.5


def normalize_mhz(freq: float) -> float:
    return round(freq, 3)


@dataclass
class ComRadio:
    active_mhz:  float = 121.800
    standby_mhz: float = 121.500
    powered:     bool  = True
    tx_enabled:  bool  = True
    rx_enabled:  bool  = True

    def swap(self) -> None:
        self.active_mhz, self.standby_mhz = self.standby_mhz, self.active_mhz


@dataclass
class AircraftState:
    callsign:      str  = 'SH001'
    aircraft_icao: str  = 'B738'
    lat:        float = 51.1537
    lon:        float = -0.1821
    alt_ft:     float = 0.0
    heading_deg:      float = 0.0
    groundspeed_kts:  float = 0.0
    vertical_speed_fpm: float = 0.0
    pitch_deg:        float = 0.0
    bank_deg:         float = 0.0
    squawk:     str  = '2000'
    ident_active: bool = False
    com1: ComRadio = field(default_factory=ComRadio)
    com2: ComRadio = field(default_factory=lambda: ComRadio(active_mhz=121.500, standby_mhz=118.000))
    ptt_com1: bool = False
    ptt_com2: bool = False
    sim_connected: bool = False
    on_ground:     bool = True


@dataclass
class ReceiverState:
    callsign:   str
    lat:        float
    lon:        float
    alt_ft:     float
    tuned_mhz:  float
    powered:    bool = True


@dataclass
class GateDecision:
    allowed:        bool
    same_frequency: bool
    in_range:       bool
    distance_nm:    float
    max_range_nm:   float
    signal_quality: float
    reason:         str


class RadioGate:
    FREQ_TOLERANCE_MHZ = 0.005
    MIN_QUALITY        = 0.02

    def can_hear(self, tx: AircraftState, rx: ReceiverState, com: int = 1) -> GateDecision:
        tx_radio = tx.com1 if com == 1 else tx.com2
        ptt = tx.ptt_com1 if com == 1 else tx.ptt_com2

        tx_freq = normalize_mhz(tx_radio.active_mhz)
        rx_freq = normalize_mhz(rx.tuned_mhz)
        same_freq = abs(tx_freq - rx_freq) <= self.FREQ_TOLERANCE_MHZ

        if not tx_radio.powered or not rx.powered:
            return GateDecision(False, same_freq, False, 0, 0, 0, 'radio_off')
        if not ptt:
            return GateDecision(False, same_freq, False, 0, 0, 0, 'ptt_not_pressed')
        if not same_freq:
            return GateDecision(False, False, False, 0, 0, 0, 'frequency_mismatch')

        dist_nm    = haversine_m(tx.lat, tx.lon, rx.lat, rx.lon) / NM_TO_M
        horizon_nm = radio_horizon_nm(tx.alt_ft) + radio_horizon_nm(rx.alt_ft)
        in_range   = dist_nm <= horizon_nm

        quality = 0.0 if horizon_nm <= 0 else max(0.0, 1.0 - (dist_nm / horizon_nm) ** 1.35)
        allowed = in_range and quality >= self.MIN_QUALITY
        reason  = 'ok' if allowed else ('out_of_range' if not in_range else 'weak_signal')
        return GateDecision(allowed, True, in_range,
                            round(dist_nm, 1), round(horizon_nm, 1),
                            round(quality, 3), reason)
