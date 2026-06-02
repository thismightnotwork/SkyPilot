from __future__ import annotations
import socket
import threading
from typing import Optional
from radio_core import AircraftState


class FSDConnection:
    """Minimal FSD TCP connection for SkyHigh.

    Sends pilot login and periodic position updates.
    Reception and full FSD protocol parsing are stubs for future work.
    """

    def __init__(self, server: str, port: int, callsign: str, cid: str, password: str, name: str):
        self.server = server
        self.port = port
        self.callsign = callsign
        self.cid = cid
        self.password = password
        self.name = name
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self._lock = threading.Lock()

    def connect(self) -> bool:
        try:
            self.sock = socket.create_connection((self.server, self.port), timeout=5)
            self.sock.settimeout(None)
            self.connected = True
            self._send(f'#AA{self.callsign}:{self.cid}:{self.password}:1:9:{self.name}\r\n')
            return True
        except Exception:
            self.connected = False
            self.sock = None
            return False

    def _send(self, data: str):
        with self._lock:
            if self.sock and self.connected:
                try:
                    self.sock.sendall(data.encode('utf-8', errors='ignore'))
                except Exception:
                    self.connected = False

    def send_position(self, state: AircraftState):
        if not self.connected:
            return
        msg = (
            f'@N:{self.callsign}:2000:4:{state.lat:.5f}:{state.lon:.5f}:'
            f'{int(state.alt_ft)}:{int(state.groundspeed_kts)}:{int(state.heading_deg)}\r\n'
        )
        self._send(msg)

    def disconnect(self):
        with self._lock:
            if self.sock:
                try:
                    self._send(f'#DP{self.callsign}\r\n')
                    self.sock.close()
                except Exception:
                    pass
            self.sock = None
            self.connected = False
