"""
mumble_radio.py — FGCom-mumble style radio voice layer for SkyHigh.
"""
from __future__ import annotations

import threading
from typing import Dict, Optional

from sim.aircraft_state import AircraftState, ReceiverState, RadioGate, GateDecision

try:
    from pymumble_py3 import Mumble, constants as mumble_const
    _MUMBLE_AVAILABLE = True
except Exception:
    _MUMBLE_AVAILABLE = False


COMMENT_PREFIX = 'SKYHIGH-RADIO'

def _encode_comment(state: AircraftState) -> str:
    return (
        f'{COMMENT_PREFIX};'
        f'CALLSIGN={state.callsign};'
        f'LAT={state.lat:.6f};LON={state.lon:.6f};ALT_FT={state.alt_ft:.1f};'
        f'COM1_FRQ={state.com1.active_mhz:.3f};'
        f'COM1_PTT={int(state.ptt_com1)};'
        f'COM1_PWR={int(state.com1.powered)};'
        f'COM2_FRQ={state.com2.active_mhz:.3f};'
        f'COM2_PTT={int(state.ptt_com2)};'
        f'COM2_PWR={int(state.com2.powered)}'
    )


class MumbleRadioClient:
    def __init__(self, host: str, username: str, password: str = '', port: int = 64738, channel: str = 'Root'):
        self.host     = host
        self.username = username
        self.password = password
        self.port     = port
        self.channel  = channel
        self._mumble:    Optional[object] = None
        self._lock       = threading.Lock()
        self._connected  = False
        self._gate       = RadioGate()
        self._receivers: Dict[str, ReceiverState] = {}
        self._tx_state:  Optional[AircraftState]  = None
        self._transmitting_com1 = False
        self._transmitting_com2 = False

    def connect(self) -> bool:
        if not _MUMBLE_AVAILABLE:
            return False
        try:
            m = Mumble(
                self.host, self.username,
                password=self.password,
                port=self.port,
                reconnect=True,
            )
            m.set_receive_sound(False)
            m.start()
            m.is_ready()
            self._mumble    = m
            self._connected = True
            try:
                m.channels.find_by_name(self.channel).move_in()
            except Exception:
                pass
            return True
        except Exception:
            return False

    def disconnect(self):
        with self._lock:
            self._connected = False
            self._mumble    = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    def set_ptt(self, com: int, active: bool):
        with self._lock:
            if com == 1:
                self._transmitting_com1 = active
            else:
                self._transmitting_com2 = active
            self._apply_mute()

    def _apply_mute(self):
        if not self._mumble or not self._connected:
            return
        tx = self._transmitting_com1 or self._transmitting_com2
        try:
            self._mumble.users.myself.mute(not tx)
        except Exception:
            pass

    def update_state(self, state: AircraftState):
        with self._lock:
            self._tx_state = state
            if not self._mumble or not self._connected:
                return
            comment = _encode_comment(state)
            try:
                self._mumble.users.myself.comment(comment)
            except Exception:
                pass

    def add_receiver(self, rx: ReceiverState):
        self._receivers[rx.callsign] = rx

    def remove_receiver(self, callsign: str):
        self._receivers.pop(callsign, None)

    def clear_receivers(self):
        self._receivers.clear()

    def compute_audibility(self, com: int = 1) -> Dict[str, GateDecision]:
        with self._lock:
            if not self._tx_state:
                return {}
            return {
                cs: self._gate.can_hear(self._tx_state, rx, com=com)
                for cs, rx in self._receivers.items()
            }
