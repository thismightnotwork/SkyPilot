# SkyHigh Pilot

A modern C++/Qt6 pilot client for the SkyHigh virtual aviation network.

## Features
- FSD protocol connection (swift-inspired logic)
- Live traffic with dead-reckoning interpolation
- Text messaging (UNICOM, private, SELCAL)
- Mumble/FGCom-style voice integration
- MSFS 2020/2024 and X-Plane sim connectors
- QML-based UI (xPilot/vPilot style)

## Building
See [docs/building.md](docs/building.md).

## Configuration
Edit `src/app/Config.h` to set your FSD and Mumble server details.
