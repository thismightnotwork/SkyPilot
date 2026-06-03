# SkyHigh Pilot ✈️

> The modern, all-in-one pilot client for the SkyHigh network.

SkyHigh Pilot bundles everything a virtual pilot needs into a single app:

- **FSD network connection** — connect to SkyHigh (or any FSD-compatible server)
- **Integrated Mumble voice** — no separate voice app; COM1/COM2 radio channels routed through your Mumble voice server
- **Model matching** — automatic aircraft model resolution with an inspectable match log
- **SimConnect bridge** — live two-way data with MSFS/P3D (X-Plane adapter planned)
- **Modern UI** — a clean, dark-mode PyQt6 interface inspired by xPilot and vPilot

---

## Architecture

```
skypilot.py          ← app entrypoint, wires all modules together
│
├── core/
│   ├── session.py       ← pilot session state (callsign, squawk, position, flight plan)
│   ├── config.py        ← persistent settings (JSON)
│   └── events.py        ← internal pub/sub event bus
│
├── network/
│   ├── fsd_client.py    ← FSD TCP connection, packet send/receive loop
│   ├── fsd_parser.py    ← packet parsing and message dispatch
│   └── fsd_protocol.py  ← packet builders (ADD, POS, PLAN, MSG, etc.)
│
├── voice/
│   ├── mumble_client.py ← Mumble protocol client (pymumble)
│   ├── radio_core.py    ← COM1/COM2 channel routing, PTT state
│   └── ptt.py           ← global PTT key liste