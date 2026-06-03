from __future__ import annotations

import socket
import threading
import time
from dataclasses import dataclass

from sim.aircraft_state import AircraftState


@dataclass
class FSDConfig:
    callsign: str
    real_name: str
    server: str
    port: int = 6809
    cid: str = "999999"
    password: str = ""
    protocol_version: str = "B"


class FSDClient:
    def __init__(self, config: FSDConfig, state: AircraftState) -> None:
        self.config = config
        self.state = state
        self.sock: socket.socket | None = None
        self._rx_thread: threading.Thread | None = None
        self._running = False
        self.connected = False
        self.last_error: str | None = None

    def connect(self) -> bool:
        try:
            self.sock = socket.create_connection((self.config.server, self.config.port), timeout=3.0)
            self.connected = True
            self._running = True
            self._send_login()
            self._send_capabilities()
            self._rx_thread = threading.Thread(target=self._reader, daemon=True)
            self._rx_thread.start()
            return True
        except OSError as exc:
            self.last_error = str(exc)
            self.connected = False
            self.sock = None
            return False

    def disconnect(self) -> None:
        self._running = False
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None

    def send_position_update(self) -> None:
        if not self.connected or not self.sock:
            return
        pbh = self._pack_pbh(self.state.pitch_deg, self.state.bank_deg, self.state.heading_deg)
        line = (
            f"@N:{self.state.callsign}:{self.state.transponder_code}:1:"
            f"{self.state.latitude_deg:.6f}:{self.state.longitude_deg:.6f}:{int(self.state.altitude_ft)}:"
            f"{int(self.state.groundspeed_kts)}:{pbh}\r\n"
        )
        self._send(line)

    def send_text(self, to: str, message: str) -> None:
        self._send(f"#TM:{self.state.callsign}:{to}:{message}\r\n")

    def request_metar(self, station: str) -> None:
        self._send(f"$AX:{self.state.callsign}:SERVER:METAR:{station}\r\n")

    def _send_login(self) -> None:
        self._send(
            f"#AA:{self.config.callsign}:{self.config.cid}:{self.config.password}:"
            f"5:{self.config.protocol_version}:{self.config.real_name}\r\n"
        )

    def _send_capabilities(self) -> None:
        self._send(f"#SB:{self.config.callsign}:PILOT:VOICE\r\n")

    def _reader(self) -> None:
        assert self.sock is not None
        self.sock.settimeout(1.0)
        last_ping = time.time()
        buf = b""
        while self._running and self.sock:
            if time.time() - last_ping > 30:
                self._send(f"$PI:{self.state.callsign}:SERVER\r\n")
                last_ping = time.time()
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    self._handle_line(line.decode(errors="ignore").strip())
            except TimeoutError:
                continue
            except OSError:
                break
        self.connected = False

    def _handle_line(self, line: str) -> None:
        if line.startswith("$PO"):
            return
        if line.startswith("#ER"):
            self.last_error = line
        elif line.startswith("#TM"):
            pass
        elif line.startswith("$CQ"):
            self._send_capabilities()

    def _send(self, line: str) -> None:
        if not self.sock:
            return
        try:
            self.sock.sendall(line.encode("utf-8"))
        except OSError as exc:
            self.last_error = str(exc)
            self.connected = False

    @staticmethod
    def _pack_pbh(pitch_deg: float, bank_deg: float, heading_deg: float) -> int:
        pitch = int((pitch_deg % 360.0) * 1024 / 360.0) & 0x3FF
        bank = int((bank_deg % 360.0) * 1024 / 360.0) & 0x3FF
        heading = int((heading_deg % 360.0) * 1024 / 360.0) & 0x3FF
        return (pitch << 22) | (bank << 12) | (heading << 2)
