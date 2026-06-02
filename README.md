# SkyPilot

**SkyPilot** is the official SkyHigh Network pilot client.  
It connects your simulator to the SkyHigh FSD server for live ATC, traffic, and radio communication.

## Architecture

| Layer | Language | Purpose |
|-------|----------|---------|
| Core app / radio / sim bridge | Python | MSFS 2020/2024 via SimConnect, radio gating, PTT |
| FSD protocol / model matching | Swift | FSD TCP connection, SQUAWK, model matching logic |
| Voice | Python + Mumble | COM1 frequency-gated VoIP via Mumble |
| UI | Qt (PySide6) | Pilot client GUI |

## Requirements

### Python
```
pip install -r requirements.txt
```

### Swift (macOS / CLI tool)
```
swift build
```

## Running

```bash
python skypilot.py --server fsd.skyhigh.aero --port 6809 --callsign SH123 --name "Luca Finnis" --cid 1234567 --password yourpassword
```

## Features
- MSFS 2020 + 2024 SimConnect integration (position, altitude, COM1)  
- Radio gating based on COM1 frequency + radio horizon range model  
- FSD protocol connection (login, position pilot, pilot disconnection)  
- Model matching for AI/multiplayer traffic  
- Mumble voice integration  
- Push-to-talk (keyboard)  
- Qt pilot client UI

## Licence
MIT — SkyHigh Network
