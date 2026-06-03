from __future__ import annotations

from dataclasses import dataclass, field
from math import asin, cos, radians, sin, sqrt
from typing import Iterable, List


@dataclass
class RadioState:
    active_mhz: float = 118.000
    standby_mhz: float = 121.500
    powered: bool = True
    ptt: bool = False


@dataclass
class RadioSnapshot:
    com1: RadioState = field(default_factory=RadioState)
    com2: RadioState = field(default_factory=lambda: RadioState(active_mhz=121.500, standby_mhz=118.000))


@dataclass
class RemoteStation:
    callsign: str
    lat: float
    lon: float
    alt_ft: float
    frequency_mhz: float
    transmitting: bool = False


@dataclass
class AircraftState:
    callsign: str
    latitude_deg: float = 51.1537
    longitude_deg: float = -0.1821
    altitude_ft: float = 0.0
    groundspeed_kts: float = 0.0
    heading_deg: float = 0.0
    pitch_deg: float = 0.0
    bank_deg: float = 0.0
    vertical_speed_fpm: float = 0.0
    on_ground: bool = True
    transponder_code: str = "7000"
    radios: RadioSnapshot = field(default_factory=RadioSnapshot)

    def swap_com(self, index: int) -> None:
        radio = self.radios.com1 if index == 1 else self.radios.com2
        radio.active_mhz, radio.standby_mhz = radio.standby_mhz, radio.active_mhz

    def set_ptt(self, index: int, pressed: bool) -> None:
        radio = self.radios.com1 if index == 1 else self.radios.com2
        radio.ptt = pressed

    def radio_horizon_nm(self) -> float:
        return 1.23 * sqrt(max(self.altitude_ft, 0.0))

    def radio_comment(self) -> str:
        return (
            "SKYHIGH-RADIO;"
            f"CALLSIGN={self.callsign};"
            f"LAT={self.latitude_deg:.6f};"
            f"LON={self.longitude_deg:.6f};"
            f"ALT_FT={self.altitude_ft:.1f};"
            f"COM1_FRQ={self.radios.com1.active_mhz:.3f};"
            f"COM1_PTT={int(self.radios.com1.ptt)};"
            f"COM1_PWR={int(self.radios.com1.powered)};"
            f"COM2_FRQ={self.radios.com2.active_mhz:.3f};"
            f"COM2_PTT={int(self.radios.com2.ptt)};"
            f"COM2_PWR={int(self.radios.com2.powered)}"
        )

    def visible_stations(self, stations: Iterable[RemoteStation]) -> List[dict]:
        out = []
        for station in stations:
            if not station.transmitting:
                continue
            if not self._freq_matches(station.frequency_mhz):
                continue
            dist = self._distance_nm(self.latitude_deg, self.longitude_deg, station.lat, station.lon)
            horizon = max(self.radio_horizon_nm(), 1.0) + 1.23 * sqrt(max(station.alt_ft, 0.0))
            quality = max(0.0, 1.0 - (dist / horizon) ** 1.35) if dist <= horizon else 0.0
            if quality < 0.02:
                continue
            out.append({
                "callsign": station.callsign,
                "frequency": station.frequency_mhz,
                "distance_nm": dist,
                "quality": quality,
            })
        return out

    def _freq_matches(self, frequency_mhz: float) -> bool:
        return any(
            abs(frequency_mhz - local) <= 0.005
            for local in (self.radios.com1.active_mhz, self.radios.com2.active_mhz)
        )

    @staticmethod
    def _distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 3440.065
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        return 2 * r * asin(sqrt(a))
