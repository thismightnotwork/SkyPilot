from __future__ import annotations
"""
Python stub that calls the Swift FSD CLI tool via subprocess for FSD protocol.
The Swift layer handles: TCP connection, login, position pilot packets, pilot disconnect.
"""
import subprocess
import threading
from pathlib import Path
from radio_core import AircraftState


SWIFT_BINARY = Path(__file__).parent / "swift_fsd" / ".build" / "release" / "SkyFSD"


class FSDConnection:
    """Drives the Swift FSD CLI binary over stdin/stdout."""

    def __init__(self, host: str, port: int, callsign: str, cid: str, password: str, name: str) -> None:
        self.host = host
        self.port = port
        self.callsign = callsign
        self.cid = cid
        self.password = password
        self.name = name
        self._proc: subprocess.Popen | None = None

    def connect(self) -> None:
        if not SWIFT_BINARY.exists():
            raise FileNotFoundError(
                f"Swift FSD binary not found at {SWIFT_BINARY}.\n"
                "Run `swift build -c release` inside the swift_fsd/ directory first."
            )
        cmd = [
            str(SWIFT_BINARY),
            "--host", self.host,
            "--port", str(self.port),
            "--callsign", self.callsign,
            "--cid", self.cid,
            "--password", self.password,
            "--name", self.name,
        ]
        self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        threading.Thread(target=self._read_loop, daemon=True).start()

    def send_position(self, state: AircraftState) -> None:
        if not self._proc or self._proc.stdin is None:
            return
        line = f"POS {state.lat:.6f} {state.lon:.6f} {state.alt_ft:.1f}\n"
        try:
            self._proc.stdin.write(line)
            self._proc.stdin.flush()
        except BrokenPipeError:
            pass

    def disconnect(self) -> None:
        if self._proc:
            try:
                self._proc.stdin.write("QUIT\n")
                self._proc.stdin.flush()
            except Exception:
                pass
            self._proc.terminate()

    def _read_loop(self) -> None:
        if not self._proc or self._proc.stdout is None:
            return
        for line in self._proc.stdout:
            print(f"[FSD] {line.rstrip()}")
