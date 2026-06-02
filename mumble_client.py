from __future__ import annotations
from typing import Dict
from radio_core import AircraftState, ReceiverState, RadioGate, GateDecision

try:
    from pymumble_py3 import Mumble
except Exception:
    Mumble = None


class SkyHighMumbleClient:
    """Mumble client for SkyHigh voice radio simulation.

    Connects to a Murmur server, publishes radio state via user comment,
    and evaluates FGCom-style frequency + range gating for each known station.
    """

    def __init__(self, host: str, username: str, password: str = '', port: int = 64738):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.mumble = None
        self.gate = RadioGate()
        self.receivers: Dict[str, ReceiverState] = {}
        self.tx_state: AircraftState | None = None
        self.transmitting = False
        self.connected = False

    def connect(self) -> bool:
        if Mumble is None:
            self.connected = False
            return False
        try:
            self.mumble = Mumble(
                self.host, self.username,
                password=self.password, port=self.port, reconnect=True,
            )
            self.mumble.set_receive_sound(False)
            self.mumble.start()
            self.mumble.is_ready()
            self.connected = True
            return True
        except Exception:
            self.connected = False
            return False

    def disconnect(self):
        self.connected = False
        self.mumble = None

    def start_transmit(self):
        self.transmitting = True

    def stop_transmit(self):
        self.transmitting = False

    def update_receiver(self, receiver: ReceiverState):
        self.receivers[receiver.callsign] = receiver

    def remove_receiver(self, callsign: str):
        self.receivers.pop(callsign, None)

    def update_tx(self, state: AircraftState):
        self.tx_state = state
        if self.connected and self.mumble:
            comment = (
                f'SKYHIGH-RADIO;CALLSIGN={state.callsign};LAT={state.lat:.6f};'
                f'LON={state.lon:.6f};ALT_FT={state.alt_ft:.1f};'
                f'COM1={state.com1_active_mhz:.3f};PTT={int(state.ptt_pressed)}'
            )
            try:
                self.mumble.users.myself.comment(comment)
            except Exception:
                pass

    def compute_audibility(self) -> Dict[str, GateDecision]:
        if not self.tx_state:
            return {}
        return {
            cs: self.gate.can_hear(self.tx_state, rx)
            for cs, rx in self.receivers.items()
        }
