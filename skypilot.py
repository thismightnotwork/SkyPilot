"""SkyPilot launcher."""

from __future__ import annotations

import argparse
import signal
import sys
import time

from audio.mumble_radio import MumbleRadioClient
from audio.ptt import PTTController
from network.fsd_client import FSDClient, FSDConfig
from sim.aircraft_state import AircraftState
from sim.simconnect_bridge import SimConnectBridge


def run_headless() -> int:
    state = AircraftState(callsign="SKY001")
    sim = SimConnectBridge(state)
    fsd = FSDClient(
        FSDConfig(
            callsign=state.callsign,
            real_name="SkyPilot User",
            server="127.0.0.1",
            port=6809,
        ),
        state,
    )
    radio = MumbleRadioClient(state)
    ptt = PTTController(state)

    sim.start()
    radio.start()
    ptt.start()
    fsd.connect()

    running = True

    def stop(*_: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    try:
        while running:
            fsd.send_position_update()
            radio.update()
            time.sleep(0.25)
    finally:
        ptt.stop()
        radio.stop()
        fsd.disconnect()
        sim.stop()

    return 0


def run_gui() -> int:
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


def main() -> int:
    parser = argparse.ArgumentParser(description="SkyPilot")
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    args = parser.parse_args()
    if args.headless:
        return run_headless()
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
