# SkyPilot

SkyPilot is a development-ready pilot client for the SkyHigh network. It is designed to track simulator state, speak FSD using a swift-inspired wire format, and expose dual-COM radio state in a way that can later be bridged through a Murmur/Mumble voice backend.

## Status

This repository is currently structured for active development before the SkyHigh FSD is online.

Implemented:
- Python package layout for simulator, network, audio, and UI modules
- MSFS SimConnect bridge with demo fallback mode
- Dual COM radio model with COM1/COM2 active + standby tracking
- FSD client scaffold using swift pilot client behaviour as protocol reference
- FGCom-mumble style radio propagation/gating helpers
- Push-to-talk handling for keyboard and optional joystick input
- PySide6 desktop UI for telemetry and radio monitoring

Planned next:
- Murmur ICE bridge for actual voice routing
- Editable COM tuning from the client UI
- ATIS / METAR display integration
- X-Plane bridge
- Packaging for Windows distribution

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the GUI client:

```bash
python skypilot.py
```

Run headless:

```bash
python skypilot.py --headless
```

## Project layout

```text
.
├── skypilot.py
├── requirements.txt
├── setup.cfg
├── docs/
│   └── ARCHITECTURE.md
├── sim/
│   ├── __init__.py
│   ├── aircraft_state.py
│   └── simconnect_bridge.py
├── network/
│   ├── __init__.py
│   └── fsd_client.py
├── audio/
│   ├── __init__.py
│   ├── mumble_radio.py
│   └── ptt.py
└── ui/
    ├── __init__.py
    └── main_window.py
```
