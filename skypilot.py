"""SkyPilot — SkyHigh Network pilot client.

Usage:
    python skypilot.py               # launch Qt GUI (default)
    python skypilot.py --headless    # headless console loop for testing
"""
from __future__ import annotations
import argparse
import sys
import time


# ────────────────────────────────────────────────────────────────────────────────
def run_headless(args: argparse.Namespace) -> None:
    from simconnect_bridge import MSFSSimBridge
    from mumble_client import SkyHighMumbleClient
    from radio_core import ReceiverState
    from ptt import PTTController
    from fsd_bridge import FSDConnection

    sim = MSFSSimBridge()
    sim_ok = sim.connect()
    print(f'[SkyPilot] SimConnect: {"ok" if sim_ok else "unavailable (demo mode)"}')

    fsd = FSDConnection(args.server, args.port, args.callsign, args.cid, args.password, args.name)
    fsd_ok = fsd.connect()
    print(f'[SkyPilot] FSD {args.server}:{args.port}: {"ok" if fsd_ok else "failed"}')

    mumble = SkyHighMumbleClient(args.mumble_server, args.callsign, port=args.mumble_port)
    mumble_ok = mumble.connect()
    print(f'[SkyPilot] Mumble {args.mumble_server}: {"ok" if mumble_ok else "failed (voice offline)"}')

    ptt = PTTController(
        hotkey=args.ptt_key,
        on_press=mumble.start_transmit,
        on_release=mumble.stop_transmit,
    )
    ptt.start()

    for cs, lat, lon, alt, freq in [
        ('EGKK_TWR', 51.1537, -0.1821, 200.0, 118.005),
        ('EGLL_APP', 51.4706, -0.4619, 4000.0, 119.730),
        ('EGKK_GND', 51.1537, -0.1821, 200.0, 121.805),
    ]:
        from radio_core import ReceiverState
        mumble.update_receiver(ReceiverState(cs, lat, lon, alt, freq))

    print('[SkyPilot] Running. Ctrl+C to quit.\n')
    try:
        while True:
            state = sim.to_aircraft_state(args.callsign, ptt.pressed)
            mumble.update_tx(state)
            if fsd_ok:
                fsd.send_position(state)
            print(
                f'{state.callsign}  {state.com1_active_mhz:.3f} MHz  '
                f'lat={state.lat:.4f} lon={state.lon:.4f}  '
                f'alt={state.alt_ft:,.0f}ft  hdg={state.heading_deg:.0f}°  '
                f'gs={state.groundspeed_kts:.0f}kt  ptt={state.ptt_pressed}'
            )
            for cs, d in mumble.compute_audibility().items():
                icon = '✓' if d.allowed else '×'
                print(f'  {icon} {cs:12s}  {d.reason:15s}  {d.distance_nm:.0f}/{d.max_range_nm:.0f}nm  q={d.signal_quality:.2f}')
            time.sleep(1.0)
    except KeyboardInterrupt:
        print('\n[SkyPilot] Shutting down...')
    finally:
        ptt.stop()
        if fsd_ok:
            fsd.disconnect()
        mumble.disconnect()
        sim.disconnect()


# ────────────────────────────────────────────────────────────────────────────────
def run_gui() -> None:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    from simconnect_bridge import MSFSSimBridge
    from mumble_client import SkyHighMumbleClient
    from radio_core import ReceiverState
    from ptt import PTTController
    from fsd_bridge import FSDConnection

    app = QApplication(sys.argv)
    win = MainWindow()

    # — Subsystems ——————————————————————————————————————————————
    sim = MSFSSimBridge()
    sim_ok = sim.connect()
    win.statusbar.showMessage(
        'SimConnect: OK' if sim_ok else 'SimConnect unavailable — running in demo mode'
    )

    ptt = PTTController(hotkey='space')
    ptt.start()

    fsd:    dict = {'conn': None, 'ok': False}
    mumble: dict = {'client': None, 'ok': False}

    default_stations = [
        ReceiverState('EGKK_TWR', 51.1537, -0.1821, 200.0,  118.005),
        ReceiverState('EGLL_APP', 51.4706, -0.4619, 4000.0, 119.730),
        ReceiverState('EGKK_GND', 51.1537, -0.1821, 200.0,  121.805),
        ReceiverState('EGLL_TWR', 51.4706, -0.4619, 200.0,  118.705),
        ReceiverState('EGTT_CTR', 51.5074, -0.1278, 500.0,  135.055),
    ]

    # — Connect / disconnect ———————————————————————————————————————
    def connect_all(server, port, callsign, cid, password, name, mserver, mport):
        conn = FSDConnection(server, port, callsign, cid, password, name)
        fsd['ok'] = conn.connect()
        fsd['conn'] = conn

        mc = SkyHighMumbleClient(mserver, callsign, port=mport)
        mumble['ok'] = mc.connect()
        mumble['client'] = mc
        for st in default_stations:
            mc.update_receiver(st)

        ptt.on_press  = mc.start_transmit
        ptt.on_release = mc.stop_transmit

        win.set_connected(fsd['ok'] or mumble['ok'])
        parts = [
            f'FSD: {"connected" if fsd["ok"] else "offline"}',
            f'Voice: {"connected" if mumble["ok"] else "offline"}',
        ]
        win.statusbar.showMessage(' · '.join(parts))

    def disconnect_all():
        if fsd.get('conn'):
            fsd['conn'].disconnect()
            fsd['conn'] = None
            fsd['ok'] = False
        if mumble.get('client'):
            mumble['client'].disconnect()
            mumble['client'] = None
            mumble['ok'] = False
        ptt.on_press = None
        ptt.on_release = None
        win.set_connected(False)
        win.statusbar.showMessage('Disconnected')

    def swap_freq():
        a = win.radio.com1_active.display.text()
        s = win.radio.com1_standby.display.text()
        try:
            af, sf = float(a), float(s)
            win.radio.update_radio(sf, af, ptt.pressed)
        except ValueError:
            pass

    # — 1-second tick ————————————————————————————————————————————————
    def tick():
        cs = win.conn.callsign.text().strip() or 'SH001'
        state = sim.to_aircraft_state(cs, ptt.pressed)
        win.radio.update_radio(state.com1_active_mhz, state.com1_standby_mhz, ptt.pressed)
        win.telemetry.update_position(state)

        rows = []
        if mumble.get('client'):
            mumble['client'].update_tx(state)
            for st in default_stations:
                d = mumble['client'].gate.can_hear(state, st)
                status = 'RX' if d.allowed else d.reason.replace('_', ' ')
                rows.append({'callsign': st.callsign, 'freq': st.tuned_mhz, 'status': status})
        else:
            for st in default_stations:
                rows.append({'callsign': st.callsign, 'freq': st.tuned_mhz, 'status': 'standby'})
        win.stations.update_rows(rows)

        if fsd.get('ok') and fsd.get('conn'):
            fsd['conn'].send_position(state)

    # — Wire signals ———————————————————————————————————————————————
    win.conn.connect_requested.connect(connect_all)
    win.conn.disconnect_requested.connect(disconnect_all)
    win.radio.swap_requested.connect(swap_freq)

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(1000)

    win.show()
    rc = app.exec()
    ptt.stop()
    disconnect_all()
    sim.disconnect()
    sys.exit(rc)


# ────────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    p = argparse.ArgumentParser(description='SkyPilot — SkyHigh Network pilot client')
    p.add_argument('--headless',      action='store_true', help='Run as headless console loop')
    p.add_argument('--server',        default='fsd.skyhigh.aero')
    p.add_argument('--port',          type=int, default=6809)
    p.add_argument('--mumble-server', default='voice.skyhigh.aero')
    p.add_argument('--mumble-port',   type=int, default=64738)
    p.add_argument('--callsign',      default='SH001')
    p.add_argument('--cid',           default='1000000')
    p.add_argument('--password',      default='')
    p.add_argument('--name',          default='Pilot')
    p.add_argument('--ptt-key',       default='space')
    args = p.parse_args()

    if args.headless:
        run_headless(args)
    else:
        run_gui()
