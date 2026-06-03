# SkyPilot

**SkyPilot** is the pilot client for the [SkyHigh Network](https://skyhigh.aero) — an independent aviation simulation network.

> **Status:** Development build — FSD server not yet live. Voice layer functional when a Murmur server is available.

---

## Features

- **SimConnect bridge** — reads position, attitude, COM1/COM2 frequencies, squawk, and on-ground state live from MSFS 2020/2024. Falls back to animated demo mode on Linux/macOS or when no sim is running.
- **FSD client** — full pilot FSD protocol (swift-project reference): login, position updates with PBH packing, keepalive, text messages, METAR requests. Ready to connect the moment SkyHigh FSD goes live — just point it at the server.
- **FGCom-mumble radio stack** — VHF line-of-sight gating (frequency match + radio horizon), dual COM1/COM2, PTT via keyboard (`Space` / `Ctrl+Space`) or joystick button. Broadcasts radio state as Mumble user comment every tick.
- **PySide6 GUI** — dark aviation-terminal theme, radio stack panel, telemetry panel, per-station signal quality table.
- **Headless mode** — `--headless` for testing without a display.

---

## Quick start

```bash
# 1. Create a venv (Python 3.10+)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch (GUI)
python skypilot.py

# 4. Or headless
python skypilot.py --headless --callsign SH001 --cid 1000000
```

SimConnect only works on Windows with MSFS running. On other platforms the client enters demo mode automatically.

---

## CLI options

| Flag | Default | Description |
|------|---------|-------------|
| `--server` | `fsd.skyhigh.aero` | FSD server hostname |
| `--port` | `6809` | FSD TCP port |
| `--mumble-server` | `voice.skyhigh.aero` | Murmur hostname |
| `--mumble-port` | `64738` | Murmur TCP/UDP port |
| `--callsign` | `SH001` | Your callsign |
| `--cid` | `1000000` | SkyHigh network CID |
| `--password` | _(empty)_ | Network password |
| `--name` | `Pilot` | Real name |
| `--ptt-key` | `space` | COM1 PTT hotkey |
| `--headless` | off | Run without GUI |

---

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a full breakdown of the FSD protocol implementation, FGCom-mumble radio gating, SimConnect variable mapping, and the development roadmap.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `PySide6` | Qt6 GUI |
| `SimConnect` | MSFS SimConnect (Windows) |
| `pymumble_py3` | Mumble voice client |
| `keyboard` | Global PTT hotkeys |
| `pygame` _(optional)_ | Joystick PTT |
| `sounddevice` + `numpy` _(optional)_ | Audio DSP (VHF effect) |

---

## Protocol references

- **FSD protocol** — [swift-project/pilotclient `fsdclient.cpp`](https://github.com/swift-project/pilotclient/blob/main/src/blackcore/fsd/fsdclient.cpp)
- **Radio gating** — [hbeni/fgcom-mumble documentation](https://github.com/hbeni/fgcom-mumble/blob/master/doc/FGCOM-mumble.md)
- **SimConnect variables** — [swift-project `simulatorfsxsimconnect.cpp`](https://github.com/swift-project/pilotclient/blob/main/src/plugins/simulator/fs/fsx/simulatorfsxsimconnect.cpp)
