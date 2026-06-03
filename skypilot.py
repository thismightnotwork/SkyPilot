"""
skypilot.py — SkyPilot entry point.

Usage:
    python skypilot.py                  # GUI (default)
    python skypilot.py --headless       # headless console mode
    python skypilot.py --help

Architecture:
  ┌────────────────────────────────────────────────────────┐
  │  skypilot.py  (entry / wiring)                        │
  ├──────────────┬──────────────────┬─────────────────────┤
  │  sim/        │  network/        │  audio/             │
  │  simconnect  │  fsd_client.py   │  mumble_radio.py    │
  │  _bridge.py  │  (FSD protocol   │  (FGCom-mumble      │
  │              │   from swift)    │   radio gating)     │
  │  aircraft    │                  │  ptt.py             │
  │  _state.py   │                  │  (keyboard/joy PTT) │
  └──────────────┴──────────────────┴─────────────────────┘
  ui/main_window.py  (PySide6 GUI)

FSD is offline at launch (SkyHigh FSD not live yet).
The client will attempt to connect and fall back gracefully to voice-only mode.
"""
from __future__ import annotations
import argparse
import sys
import time

from sim.aircraft_state import AircraftState, ReceiverState
from sim.simconnect_bridge import MSFSSimBridge
from network.fsd_client import FSDClient, FSDCallbacks, SquawkMode
from audio.mumble_radio import MumbleRadioClient
from audio.ptt import PTTController

DEMO_STATIONS = [
    ReceiverState('EGKK_TWR', 51.1537, -0.1821, 200.0,  118.005),
    ReceiverState('EGLL_APP', 51.4706, -0.4619, 4000.0, 119.730),
    ReceiverState('EGKK_GND', 51.1537, -0.1821, 200.0,  121.805),
    ReceiverState('EGLL_TWR', 51.4706, -0.4619, 200.0,  118.705),
    ReceiverState('EGTT_CTR', 51.5074, -0.1278, 500.0,  135.055),
    ReceiverState('EGSS_APP', 51.8850,  0.2350, 4000.0, 128.525),
    ReceiverState('EGCC_TWR', 53.3537, -2.2750, 200.0,  118.625),
    ReceiverState('EGGD_TWR', 51.3826, -2.7191, 200.0,  133.850),
]


def run_headless(args: argparse.Namespace) -> None:
    sim    = MSFSSimBridge()
    sim_ok = sim.connect()
    print(f'[SkyPilot] SimConnect: {"ok" if sim_ok else "unavailable — demo mode"}')

    cb = FSDCallbacks(
        on_connected    = lambda cs: print(f'[FSD] Connected as {cs}'),
        on_disconnected = lambda r:  print(f'[FSD] Disconnected: {r}'),
        on_text_message = lambda f, t, m: print(f'[MSG] {f} → {t}: {m}'),
        on_server_error = lambda c, m: print(f'[FSD ERR {c}] {m}'),
    )
    fsd    = FSDClient(args.server, args.port, args.callsign, args.cid,
                       args.password, args.name, callbacks=cb)
    fsd_ok = fsd.connect()
    print(f'[SkyPilot] FSD {args.server}:{args.port}: {"ok" if fsd_ok else "offline (FSD not yet live)"}')

    mumble    = MumbleRadioClient(args.mumble_server, args.callsign, port=args.mumble_port)
    mumble_ok = mumble.connect()
    print(f'[SkyPilot] Mumble {args.mumble_server}: {"ok" if mumble_ok else "offline"}')

    for rx in DEMO_STATIONS:
        mumble.add_receiver(rx)

    ptt = PTTController()
    ptt.bind('com1', hotkey=args.ptt_key)
    ptt.bind('com2', hotkey='ctrl+space')

    def on_ptt_change(channel: str, pressed: bool):
        if channel == 'com1':
            mumble.set_ptt(1, pressed)
        elif channel == 'com2':
            mumble.set_ptt(2, pressed)

    ptt.on_change = on_ptt_change
    ptt.start()

    print('[SkyPilot] Running.  Ctrl+C to quit.\n')
    try:
        while True:
            ptt_com1 = ptt.is_pressed('com1')
            ptt_com2 = ptt.is_pressed('com2')
            state = sim.get_state(args.callsign, ptt_com1=ptt_com1, ptt_com2=ptt_com2)
            mumble.update_state(state)
            if fsd_ok:
                fsd.send_position(state)

            print(
                f'{state.callsign:8s}  '
                f'COM1={state.com1.active_mhz:.3f}  COM2={state.com2.active_mhz:.3f}  '
                f'lat={state.lat:.4f}  lon={state.lon:.4f}  '
                f'alt={state.alt_ft:,.0f}ft  hdg={state.heading_deg:.0f}°  '
                f'gs={state.groundspeed_kts:.0f}kt  '
                f'ptt1={ptt_com1} ptt2={ptt_com2}'
            )
            for cs, d in mumble.compute_audibility(com=1).items():
                icon = '✓' if d.allowed else '×'
                print(f'  {icon} {cs:12s}  {d.reason:16s}  '
                      f'{d.distance_nm:.0f}/{d.max_range_nm:.0f}nm  q={d.signal_quality:.2f}')
            time.sleep(1.0)

    except KeyboardInterrupt:
        print('\n[SkyPilot] Shutting down…')
    finally:
        ptt.stop()
        fsd.disconnect()
        mumble.disconnect()
        sim.disconnect()


def run_gui() -> None:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    win = MainWindow()

    sim = MSFSSimBridge()
    sim_ok = sim.connect()
    win.statusbar.showMessage(
        'SimConnect OK' if sim_ok else 'SimConnect unavailable — demo mode'
    )

    ptt = PTTController()
    ptt.bind('com1', hotkey='space')
    ptt.bind('com2', hotkey='ctrl+space')
    ptt.start()

    fsd_state    = {'client': None, 'ok': False}
    mumble_state = {'client': None, 'ok': False}

    def connect_all(fsd_host, fsd_port, callsign, cid, password, name, voice_host, voice_port):
        cb = FSDCallbacks(
            on_connected    = lambda cs: win.statusbar.showMessage(f'FSD connected as {cs}'),
            on_disconnected = lambda r:  win.statusbar.showMessage(f'FSD disconnected: {r}'),
            on_text_message = lambda f, t, m: print(f'[MSG] {f}: {m}'),
            on_server_error = lambda c, m: win.statusbar.showMessage(f'FSD error {c}: {m}'),
        )
        fsd = FSDClient(fsd_host, fsd_port, callsign, cid, password, name, callbacks=cb)
        fsd_state['ok']     = fsd.connect()
        fsd_state['client'] = fsd

        mc = MumbleRadioClient(voice_host, callsign, port=voice_port)
        mumble_state['ok']     = mc.connect()
        mumble_state['client'] = mc
        for rx in DEMO_STATIONS:
            mc.add_receiver(rx)

        def on_ptt(channel: str, pressed: bool):
            if channel == 'com1':
                mc.set_ptt(1, pressed)
            elif channel == 'com2':
                mc.set_ptt(2, pressed)

        ptt.on_change = on_ptt

        win.set_connected(fsd_state['ok'] or mumble_state['ok'])
        parts = [
            f'FSD: {"connected" if fsd_state["ok"] else "offline (not yet live)"}',
            f'Voice: {"connected" if mumble_state["ok"] else "offline"}',
        ]
        win.statusbar.showMessage(' · '.join(parts))

    def disconnect_all():
        c = fsd_state.get('client')
        if c:
            c.disconnect()
        fsd_state.update(client=None, ok=False)

        m = mumble_state.get('client')
        if m:
            m.disconnect()
        mumble_state.update(client=None, ok=False)

        ptt.on_change = None
        win.set_connected(False)
        win.statusbar.showMessage('Disconnected')

    def swap_com1():
        a = win.radio._active_com1.value_mhz
        s = win.radio._standby_com1.value_mhz
        win.radio.update_com(1, s, a, ptt.is_pressed('com1'), False)

    def swap_com2():
        a = win.radio._active_com2.value_mhz
        s = win.radio._standby_com2.value_mhz
        win.radio.update_com(2, s, a, ptt.is_pressed('com2'), False)

    def tick():
        cs      = win.conn.callsign.text().strip() or 'SH001'
        ptt1    = ptt.is_pressed('com1')
        ptt2    = ptt.is_pressed('com2')
        state   = sim.get_state(cs, ptt_com1=ptt1, ptt_com2=ptt2)

        if not sim_ok:
            state.com1.active_mhz  = win.radio._active_com1.value_mhz
            state.com1.standby_mhz = win.radio._standby_com1.value_mhz
            state.com2.active_mhz  = win.radio._active_com2.value_mhz
            state.com2.standby_mhz = win.radio._standby_com2.value_mhz

        mc = mumble_state.get('client')
        if mc:
            mc.update_state(state)
            aud1 = mc.compute_audibility(com=1)
        else:
            aud1 = {}

        has_rx_com1 = any(d.allowed for d in aud1.values())
        win.radio.update_com(1, state.com1.active_mhz, state.com1.standby_mhz, ptt1, has_rx_com1)
        win.radio.update_com(2, state.com2.active_mhz, state.com2.standby_mhz, ptt2, False)
        win.tele.update(state)

        rows = []
        if mc:
            for cs_rx, d in aud1.items():
                rx = mc._receivers.get(cs_rx)
                rows.append({
                    'callsign': cs_rx,
                    'freq':     rx.tuned_mhz if rx else 0.0,
                    'status':   'RX' if d.allowed else d.reason.replace('_', ' '),
                    'dist_nm':  d.distance_nm,
                    'quality':  d.signal_quality,
                })
        else:
            for rx in DEMO_STATIONS[:8]:
                rows.append({'callsign': rx.callsign, 'freq': rx.tuned_mhz, 'status': 'standby',
                             'dist_nm': 0, 'quality': 0})
        win.stations.update_rows(rows)

        if fsd_state.get('ok') and fsd_state.get('client'):
            fsd_state['client'].send_position(state)

    win.conn.connect_requested.connect(connect_all)
    win.conn.disconnect_requested.connect(disconnect_all)
    win.radio.swap_com1_requested.connect(swap_com1)
    win.radio.swap_com2_requested.connect(swap_com2)

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(1000)

    win.show()
    rc = app.exec()
    ptt.stop()
    disconnect_all()
    sim.disconnect()
    sys.exit(rc)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='SkyPilot — SkyHigh Network pilot client')
    p.add_argument('--headless',      action='store_true')
    p.add_argument('--server',        default='fsd.skyhigh.aero')
    p.add_argument('--port',          type=int, default=6809)
    p.add_argument('--mumble-server', default='voice.skyhigh.aero',  dest='mumble_server')
    p.add_argument('--mumble-port',   type=int, default=64738,        dest='mumble_port')
    p.add_argument('--callsign',      default='SH001')
    p.add_argument('--cid',           default='1000000')
    p.add_argument('--password',      default='')
    p.add_argument('--name',          default='Pilot')
    p.add_argument('--ptt-key',       default='space',                dest='ptt_key')
    args = p.parse_args()

    if args.headless:
        run_headless(args)
    else:
        run_gui()
