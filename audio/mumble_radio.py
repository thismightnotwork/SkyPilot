from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from sim.aircraft_state import AircraftState, RemoteStation


@dataclass
class MumbleRadioClient:
    state: AircraftState
    host: str = "127.0.0.1"
    port: int = 64738
    channel: str = "SkyHigh"
    running: bool = False
    stations: List[RemoteStation] = field(default_factory=list)

    def start(self) -> None:
        self.running = True
        self.stations = [
            RemoteStation("SH_DEL", 51.4775, -0.4614, 100.0, 121.805, True),
            RemoteStation("SH_APP", 51.1530, -0.1900, 3000.0, 118.000, True),
            RemoteStation("SH_GND", 51.1470, -0.1830, 80.0, 121.500, False),
        ]

    def stop(self) -> None:
        self.running = False

    def update(self) -> None:
        if not self.running:
            return
        _ = self.state.radio_comment()

    def visible_stations(self) -> list[dict]:
        return self.state.visible_stations(self.stations)
