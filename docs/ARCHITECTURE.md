# SkyPilot architecture

## Goals

SkyPilot is intended to become a pilot client for the SkyHigh network with three major subsystems:
- simulator state ingestion
- FSD network communication
- radio/voice distribution

## Protocol direction

The FSD implementation is modelled after behaviour used by the swift pilot client project. The current code keeps the message framing and PBH packing isolated so it can be swapped or extended when the real network server is available.

The radio model follows FGCom-style concepts:
- COM1 and COM2 both carry active and standby frequencies
- signal quality is based on altitude-derived horizon and distance
- radio power and push-to-talk state are explicit inputs

## Development phases

1. Simulator integration and UI
2. FSD login / heartbeat / position reporting
3. Voice metadata publication to Mumble
4. Server-side Murmur ICE routing
5. Packaging and deployment
