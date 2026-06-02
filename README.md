# SkyPilot

**SkyPilot** is the SkyHigh Network pilot client.

Built in Python with PySide6, it connects your simulator to the SkyHigh FSD server for live ATC, traffic, and radio communication. The UI is styled after xPilot and the radio system is modelled after FGCom-mumble.

## Architecture

| Layer | Stack | Purpose |
|---|---|---|
| Desktop shell | Python + PySide6 | xPilot-style dark operational UI |
| Simulator bridge | Python + SimConnect | MSFS 2020 · MSFS 2024 position, heading, GS, COM1 |
| Radio core | Python | COM frequency match, line-of-sight range gating, PTT |
| Voice transport | Python + pymumble_py3 | Mumble connection, radio state publishing |
| Network bridge | Python | FSD TCP login, periodic position sending |

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
# GUI (default)
python skypilot.py

# Headless console loop (testing / no display)
python skypilot.py --headless --server fsd.skyhigh.aero --callsign SH123
```

## Features

- xPilot-inspired dark UI: large COM1 frequency display, TX/RX badges, swap button, station list
- MSFS 2020 · 2024 via SimConnect with automatic demo-mode fallback if sim is offline
- Radio gating by COM1 frequency match and radio-horizon range model (FGCom-style)
- PTT on Spacebar (configurable), wired to Mumble transmit state
- FSD login and position update loop
- Station cards showing RX / out of range / standby state per tuned frequency

## Development

Branch strategy: `feature/*` branches, small commits, draft PRs against `main`.

| File | Purpose |
|---|---|
| `skypilot.py` | Entry point, GUI loop, headless loop |
| `ui/main_window.py` | PySide6 xPilot-style window and all panels |
| `radio_core.py` | AircraftState, ReceiverState, RadioGate, haversine |
| `simconnect_bridge.py` | MSFS SimConnect adapter with demo fallback |
| `mumble_client.py` | Mumble client wrapper and radio-state publisher |
| `fsd_bridge.py` | FSD TCP connection and position sender |
| `ptt.py` | Keyboard PTT controller |

## Licence

MIT — SkyHigh Network
