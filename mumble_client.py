from __future__ import annotations
import threading
import time
from typing import Dict, Optional

from radio_core import AircraftState, ReceiverState, RadioGate, GateDecision

try:
    from pymumble_py3 import Mumble
    _MUMBLE_AVAILABLE = True
except ImportError:
    _MUMBLE_AVAILABLE = False


class SkyHighMumbleClient:
    """
    Wraps a pymumble connection and applies SkyHigh radio gating.

    Architecture note
    -----------------
    True per-stream audio suppression inside one shared Mumble channel requires
    a native Mumble plugin (like FGCom-mumble uses). This client handles the
    Python-accessible layer: frequency gating decisions, state publishing, and
    PTT mic control. For a production deployment use one Mumble channel per
    active frequency sector, and route users to the correct channel server-side
    based on their tuned COM1 frequency reported via the FSD/radio state.
    """

    POLL_INTERVAL = 0.5

    def __init__(self, host: str, user: str, password: str = "", port: int = 64738) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._mumble: Optional[Mumble] = None
        self._gate = RadioGate()
        self._tx_state: Optional[AircraftState] = None
        self._receivers: Dict[str, ReceiverState] = {}
        self._lock = threading.Lock()
        self._running = False

    def connect(self) -> None:
        if not _MUMBLE_AVAILABLE:
            raise RuntimeError("pymumble_py3 not installed. Run: pip install pymumble_py3")
        self._mumble = Mumble(self.host, self.user, password=self.password, port=self.port, reconnect=True)
        self._mumble.set_receive_sound(False)
        self._mumble.start()
        self._mumble.is_ready()
        self._running = True
        threading.Thread(target=self._poll_loop, daemon=True).start()

    def disconnect(self) -> None:
        self._running = False
        if self._mumble:
            self._mumble.stop()

    def update_tx(self, state: AircraftState) -> None:
        with self._lock:
            self._tx_state = state
        self._publish_comment(state)

    def update_receiver(self, rx: ReceiverState) -> None:
        with self._lock:
            self._receivers[rx.callsign] = rx

    def compute_audibility(self) -> Dict[str, GateDecision]:
        with self._lock:
            tx = self._tx_state
            receivers = dict(self._receivers)
        if not tx:
            return {}
        return {cs: self._gate.can_hear(tx, rx) for cs, rx in receivers.items()}

    def start_transmit(self) -> None:
        if self._mumble:
            self._mumble.users.myself.unmute()

    def stop_transmit(self) -> None:
        if self._mumble:
            self._mumble.users.myself.mute()

    def _publish_comment(self, state: AircraftState) -> None:
        if not self._mumble:
            return
        comment = (
            f"SKYHIGH;CALLSIGN={state.callsign};LAT={state.lat:.6f};LON={state.lon:.6f};"
            f"ALT={state.alt_ft:.1f};COM1={state.com1_active_mhz:.3f};PTT={int(state.ptt_pressed)}"
        )
        try:
            self._mumble.users.myself.comment(comment)
        except Exception:
            pass

    def _poll_loop(self) -> None:
        while self._running:
            self.compute_audibility()
            time.sleep(self.POLL_INTERVAL)
