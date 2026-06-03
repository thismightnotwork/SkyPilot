from __future__ import annotations

import random
import threading
import time

from sim.aircraft_state import AircraftState


class SimConnectBridge:
    """Simple simulator bridge with demo fallback.

    Replace the demo loop with real SimConnect bindings during active development.
    """

    def __init__(self, state: AircraftState, interval: float = 0.25) -> None:
        self.state = state
        self.interval = interval
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _run(self) -> None:
        t = 0.0
        while self._running:
            t += self.interval
            self.state.heading_deg = (self.state.heading_deg + 0.8) % 360.0
            self.state.groundspeed_kts = 110 + 15 * (0.5 + 0.5 * __import__("math").sin(t / 6))
            self.state.altitude_ft = max(0.0, 2500 + 800 * __import__("math").sin(t / 10))
            self.state.vertical_speed_fpm = 400 * __import__("math").cos(t / 10)
            self.state.pitch_deg = 2.5 * __import__("math").sin(t / 4)
            self.state.bank_deg = 8.0 * __import__("math").sin(t / 5)
            self.state.latitude_deg += random.uniform(-0.00015, 0.00015)
            self.state.longitude_deg += random.uniform(-0.00015, 0.00015)
            self.state.on_ground = self.state.altitude_ft < 80
            time.sleep(self.interval)
