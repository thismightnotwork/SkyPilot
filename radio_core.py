from __future__ import annotations
from dataclasses import dataclass
from math import radians, sin, cos, sqrt, atan2
from typing import Optional

EARTH_RADIUS_M = 6_371_000.0
NM_TO_M = 1_852.0


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dl = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * atan2(sqrt(a), sqrt(1 - a))


def radio_horizon_nm(alt_ft: float) -> float:
    """Line-of-sight radio horizon in NM for a given altitude (ft)."""
    alt_ft = max(0.0, alt_ft)
    return 1.23 * (alt_ft ** 0.5)


def normalize_freq(freq_mhz: float) -> float:
    return round(freq_mhz, 3)


@dataclass
class AircraftState:
    callsign: str
    lat: float
    lon: float
    alt_ft: float
    com1_active_mhz: float
    com1_standby_mhz: float = 121.500
    ptt_pressed: bool = False
    radio_powered: bool = True


@dataclass
class ReceiverState:
    callsign: str
    lat: float
    lon: float
    alt_ft: float
    tuned_mhz: float
    radio_powered: bool = True


@dataclass
class GateDecision:
    allowed: bool
    same_frequency: bool
    in_range: bool
    distance_nm: float
    max_range_nm: float
    signal_quality: float
    reason: str


class RadioGate:
    FREQ_TOLERANCE_MHZ = 0.005
    MIN_QUALITY = 0.02

    def can_hear(self, tx: AircraftState, rx: ReceiverState) -> GateDecision:
        tx_freq = normalize_freq(tx.com1_active_mhz)
        rx_freq = normalize_freq(rx.tuned_mhz)
        same_freq = abs(tx_freq - rx_freq) <= self.FREQ_TOLERANCE_MHZ

        if not tx.radio_powered or not rx.radio_powered:
            return GateDecision(False, same_freq, False, 0.0, 0.0, 0.0, "radio_off")
        if not tx.ptt_pressed:
            return GateDecision(False, same_freq, False, 0.0, 0.0, 0.0, "ptt_not_pressed")
        if not same_freq:
            return GateDecision(False, False, False, 0.0, 0.0, 0.0, "frequency_mismatch")

        dist_nm = haversine_m(tx.lat, tx.lon, rx.lat, rx.lon) / NM_TO_M
        max_range_nm = radio_horizon_nm(tx.alt_ft) + radio_horizon_nm(rx.alt_ft)
        in_range = dist_nm <= max_range_nm
        quality = max(0.0, 1.0 - (dist_nm / max(max_range_nm, 1.0)) ** 1.35) if in_range else 0.0
        allowed = in_range and quality >= self.MIN_QUALITY
        reason = "ok" if allowed else ("out_of_range" if not in_range else "weak_signal")
        return GateDecision(allowed, True, in_range, round(dist_nm, 2), round(max_range_nm, 2), round(quality, 3), reason)
