from __future__ import annotations

import threading
import time

from sim.aircraft_state import AircraftState

try:
    import pygame
except Exception:
    pygame = None


class PTTController:
    def __init__(self, state: AircraftState) -> None:
        self.state = state
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def set_channel(self, channel: int, pressed: bool) -> None:
        self.state.set_ptt(channel, pressed)

    def _poll(self) -> None:
        if pygame is None:
            while self._running:
                time.sleep(0.1)
            return
        pygame.init()
        pygame.joystick.init()
        while self._running:
            pygame.event.pump()
            time.sleep(1 / 30)
