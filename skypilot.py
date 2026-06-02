"""
SkyPilot — SkyHigh Network pilot client entry point.

Usage:
    python skypilot.py                          # launch Qt UI
    python skypilot.py --headless [args...]     # headless demo loop
"""
from __future__ import annotations
import argparse
import sys
import time


def run_headless(args):
    from simconnect_bridge import MSFSSimBridge
    from mumble_client import SkyHighMumbleClient
    from radio_core import ReceiverState
    from ptt import PTTController
    from fsd_bridge import FSDConnection

    sim = MSFSSimBridge()
    sim.connect()
    print("[SkyPilot] Connected to MSFS")

    fsd = FSDConnection(args.server, args.port, args.callsign, args.cid, args.password, args.name)
    fsd.connect()
    print(f"[SkyPilot] Connected to FSD: {args.server}:{args.port}")

    mumble = SkyHighMumbleClient(args.mumble_server, args.callsign, port=args.mumble_port)
    mumble.connect()
    print(f"[SkyPilot] Connected to Mumble: {args.mumble_server}")

    ptt = PTTController(
        hotkey=args.ptt_key,
        on_press=mumble.start_transmit,
        on_release=mumble.stop_transmit,
    )
    ptt.start()

    mumble.update_receiver(ReceiverState("EGKK_TWR", 51.1537, -0.1821, 200.0, 118.005))
    mumble.update_receiver(ReceiverState("EGLL_APP", 51.4706, -0.4619, 4000.0, 119.730))

    print("[SkyPilot] Running. Ctrl+C to quit.")
    try:
        while True:
            state = sim.to_aircraft_state(args.callsign, ptt.pressed)
            mumble.update_tx(state)
            fsd.send_position(state)
            for cs, d in mumble.compute_audibility().items():
                print(f"  {cs}: {d.reason} ({d.distance_nm:.0f}/{d.max_range_nm:.0f} nm, q={d.signal_quality:.2f})")
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[SkyPilot] Shutting down...")
        fsd.disconnect()
        mumble.disconnect()
        sim.disconnect()


def run_gui():
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--headless", action="store_true")
    p.add_argument("--server", default="fsd.skyhigh.aero")
    p.add_argument("--port", type=int, default=6809)
    p.add_argument("--mumble-server", default="voice.skyhigh.aero")
    p.add_argument("--mumble-port", type=int, default=64738)
    p.add_argument("--callsign", default="SH001")
    p.add_argument("--cid", default="1000000")
    p.add_argument("--password", default="")
    p.add_argument("--name", default="Pilot")
    p.add_argument("--ptt-key", default="space")
    args = p.parse_args()

    if args.headless:
        run_headless(args)
    else:
        run_gui()
