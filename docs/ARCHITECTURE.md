# SkyPilot — Architecture

## Overview

```
skypilot.py  ──── wires everything together (GUI + headless modes)
│
├── sim/
│   ├── aircraft_state.py   Data models: AircraftState, ComRadio, ReceiverState,
│   │                       RadioGate, GateDecision  (FGCom-mumble gating logic)
│   └── simconnect_bridge.py  MSFS 2020/2024 SimConnect reader (4 Hz poll thread)
│                              Falls back to animated demo mode when sim unavailable
│
├── network/
│   └── fsd_client.py       Full FSD TCP client (swift-project protocol reference)
│                            Implements: #AA login, @N/@S position, $PI keepalive,
│                            #TM text, $AX METAR, PBH packing, inbound parser.
│                            Gracefully offline until SkyHigh FSD goes live.
│
├── audio/
│   ├── mumble_radio.py     FGCom-mumble style Mumble client.
│   │                       Broadcasts radio state as user comment every tick.
│   │                       Controls PTT via mute/unmute.
│   │                       Exposes compute_audibility() for per-station gating.
│   └── ptt.py              Multi-channel PTT (COM1 + COM2).
│                            Keyboard hotkeys (keyboard package).
│                            Optional joystick button (pygame).
│
└── ui/
    └── main_window.py      PySide6 dark-theme GUI.
                            Panels: Connection, Radio Stack (COM1+COM2), Telemetry,
                            Stations table with distance + signal quality.
```

## FSD Protocol (swift reference)

The FSD client implements the protocol documented and implemented in
[swift-project/pilotclient](https://github.com/swift-project/pilotclient).

## Radio Stack (FGCom-mumble reference)

Gating logic in `sim/aircraft_state.py → RadioGate` mirrors
[FGCom-mumble's radio range model](https://github.com/hbeni/fgcom-mumble/blob/master/doc/FGCOM-mumble.md):

1. Both radios must be powered.
2. PTT must be pressed on the transmitting side.
3. `|tx_freq - rx_freq| ≤ 0.005 MHz`.
4. `distance ≤ radio_horizon(tx_alt) + radio_horizon(rx_alt)`
5. `signal_quality = max(0, 1 - (dist / max_range)^1.35)`.
6. Transmission allowed when `quality ≥ 0.02`.

## SimConnect Variables

Mirrors swift-project variable set:
- `PLANE_LATITUDE` / `LONGITUDE` / `ALTITUDE`
- `PLANE_HEADING_DEGREES_TRUE`
- `GROUND_VELOCITY`
- `VERTICAL_SPEED`
- `PLANE_PITCH_DEGREES` / `PLANE_BANK_DEGREES`
- `SIM_ON_GROUND`
- `TRANSPONDER_CODE:1`
- `COM_ACTIVE_FREQUENCY:1` / `:2`
- `COM_STANDBY_FREQUENCY:1` / `:2`

## FSD Not Yet Live

`FSDClient.connect()` returns `False` gracefully and the client continues in
voice-only mode. Set `fsd.skyhigh.aero` to the real FSD host when SkyHigh goes live.

## Development Roadmap

- [ ] Murmur ICE bot for server-side audio routing
- [ ] Inbound pilot position rendering (other traffic on map panel)
- [ ] ATIS / METAR display panel
- [ ] COM frequency input widget (click-to-edit freq display)
- [ ] Squawk + transponder panel
- [ ] Aircraft model reporting (`$CQ ICAOEQ`)
- [ ] X-Plane 12 bridge (XPlaneConnect or XPUIPC)
- [ ] Audio DSP: VHF effect + white noise based on signal quality
- [ ] Installer (PyInstaller one-file exe for Windows)
