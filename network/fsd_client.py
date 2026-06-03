"""
fsd_client.py — Full FSD (Flight Simulator Daemon) client for SkyHigh.
"""
from __future__ import annotations

import select
import socket
import threading
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Optional

from sim.aircraft_state import AircraftState

FSD_ENCODING  = 'utf-8'
FSD_EOL       = '\r\n'
KEEPALIVE_SEC = 30
POS_UPDATE_SEC = 5


class SquawkMode(IntEnum):
    STANDBY = 0
    NORMAL  = 1
    IDENT   = 2


class PilotRating(IntEnum):
    STUDENT = 1
    PPL     = 2
    IR      = 3
    CMEL    = 4
    ATP     = 5
    FERRY   = 6
    MILITARY= 7


def pack_pbh(pitch: float, bank: float, hdg: float) -> int:
    p = max(-90.0, min(90.0, pitch))
    b = max(-180.0, min(180.0, bank))
    h = hdg % 360.0
    p_enc = int((p + 90.0)  / 180.0 * 1023) & 0x3FF
    b_enc = int((b + 180.0) / 360.0 * 1023) & 0x3FF
    h_enc = int(h            / 360.0 * 1023) & 0x3FF
    return (p_enc << 22) | (b_enc << 12) | (h_enc << 2)


@dataclass
class FSDCallbacks:
    on_connected:    Optional[Callable[[str], None]]           = None
    on_disconnected: Optional[Callable[[str], None]]           = None
    on_text_message: Optional[Callable[[str, str, str], None]] = None
    on_pilot_pos:    Optional[Callable[[dict], None]]          = None
    on_metar:        Optional[Callable[[str, str], None]]      = None
    on_capabilities: Optional[Callable[[str, str], None]]      = None
    on_server_error: Optional[Callable[[int, str], None]]      = None


class FSDClient:
    CLIENT_NAME    = 'SkyPilot'
    CLIENT_VERSION = '0.1.0'
    CLIENT_ID      = 'SP01'

    def __init__(self, host: str, port: int, callsign: str, cid: str, password: str,
                 real_name: str, rating: PilotRating = PilotRating.STUDENT,
                 callbacks: Optional[FSDCallbacks] = None):
        self.host      = host
        self.port      = port
        self.callsign  = callsign.upper()
        self.cid       = cid
        self.password  = password
        self.real_name = real_name
        self.rating    = rating
        self.cb        = callbacks or FSDCallbacks()
        self._sock     = None
        self._lock     = threading.Lock()
        self._reader   = None
        self._running  = False
        self._connected= False
        self._last_ping= 0.0
        self._last_pos = 0.0
        self._recv_buf = ''

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=8)
            self._sock.settimeout(None)
            self._running   = True
            self._connected = True
            self._reader    = threading.Thread(target=self._read_loop, daemon=True)
            self._reader.start()
            self._login()
            if self.cb.on_connected:
                self.cb.on_connected(self.callsign)
            return True
        except Exception:
            self._connected = False
            return False

    def disconnect(self, reason: str = 'normal'):
        if self._connected:
            self._raw_send(f'#DP{self.callsign}{FSD_EOL}')
        self._running   = False
        self._connected = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        if self.cb.on_disconnected:
            self.cb.on_disconnected(reason)

    def send_position(self, state: AircraftState, mode: SquawkMode = SquawkMode.NORMAL) -> bool:
        if not self._connected:
            return False
        now = time.monotonic()
        interval = POS_UPDATE_SEC if not state.on_ground else POS_UPDATE_SEC * 3
        if now - self._last_pos < interval:
            return False
        self._last_pos = now
        self._keepalive()

        flag = 'S' if mode == SquawkMode.STANDBY else 'N'
        pbh  = pack_pbh(state.pitch_deg, state.bank_deg, state.heading_deg)
        msg = (
            f'@{flag}:{self.callsign}:{state.squawk}:{int(self.rating)}:'
            f'{state.lat:.6f}:{state.lon:.6f}:'
            f'{int(state.alt_ft)}:{int(state.groundspeed_kts)}:{pbh}\r\n'
        )
        self._raw_send(msg)
        return True

    def send_text(self, to: str, text: str):
        self._raw_send(f'#TM{self.callsign}:{to}:{text}{FSD_EOL}')

    def request_metar(self, icao: str):
        self._raw_send(f'$AX{self.callsign}:SERVER:METAR:{icao.upper()}{FSD_EOL}')

    def request_atis(self, atc_callsign: str):
        self._raw_send(f'$CQ{self.callsign}:{atc_callsign}:ATIS{FSD_EOL}')

    def _login(self):
        caps = 'VERSION=1:ATCINFO=1:INTERIMPOS=1:ICAOEQ=1'
        self._raw_send(
            f'#AA{self.callsign}:{self.cid}:{self.password}:{int(self.rating)}:9:{self.real_name}{FSD_EOL}'
        )
        self._raw_send(
            f'#SB{self.callsign}:SERVER:CAPS:{caps}{FSD_EOL}'
        )

    def _keepalive(self):
        now = time.monotonic()
        if now - self._last_ping > KEEPALIVE_SEC:
            self._last_ping = now
            token = str(int(now * 1000) % 100000)
            self._raw_send(f'$PI{self.callsign}:SERVER:{token}{FSD_EOL}')

    def _raw_send(self, data: str):
        with self._lock:
            if self._sock and self._connected:
                try:
                    self._sock.sendall(data.encode(FSD_ENCODING, errors='replace'))
                except Exception:
                    self._connected = False

    def _read_loop(self):
        while self._running:
            try:
                ready = select.select([self._sock], [], [], 1.0)[0]
                if not ready:
                    continue
                chunk = self._sock.recv(4096).decode(FSD_ENCODING, errors='replace')
                if not chunk:
                    break
                self._recv_buf += chunk
                while '\r\n' in self._recv_buf or '\n' in self._recv_buf:
                    sep = '\r\n' if '\r\n' in self._recv_buf else '\n'
                    line, self._recv_buf = self._recv_buf.split(sep, 1)
                    if line:
                        self._dispatch(line.strip())
            except Exception:
                break
        self._connected = False
        if self.cb.on_disconnected:
            self.cb.on_disconnected('connection_lost')

    def _dispatch(self, line: str):
        if not line:
            return
        if line.startswith('$PO'):
            return
        if line.startswith('$ER'):
            parts = line.split(':', 3)
            if self.cb.on_server_error:
                code = int(parts[2]) if len(parts) > 2 else -1
                msg  = parts[3] if len(parts) > 3 else ''
                self.cb.on_server_error(code, msg)
            return
        if line.startswith('#TM'):
            parts = line[3:].split(':', 2)
            if len(parts) == 3 and self.cb.on_text_message:
                self.cb.on_text_message(parts[0], parts[1], parts[2])
            return
        if line.startswith('@'):
            self._parse_pilot_pos(line)
            return
        if line.startswith('$AR') and ':METAR:' in line:
            parts = line.split(':METAR:', 1)
            if len(parts) == 2 and self.cb.on_metar:
                icao = parts[0].split(':')[-1]
                self.cb.on_metar(icao, parts[1])
            return
        if line.startswith('$CR') and ':CAPS:' in line:
            parts = line.split(':')
            cs   = parts[1] if len(parts) > 1 else ''
            caps = parts[3] if len(parts) > 3 else ''
            if self.cb.on_capabilities:
                self.cb.on_capabilities(cs, caps)
            return

    def _parse_pilot_pos(self, line: str):
        try:
            parts = line.split(':')
            if len(parts) < 9:
                return
            d = {
                'mode':     line[1],
                'callsign': parts[1],
                'squawk':   parts[2],
                'rating':   int(parts[3]),
                'lat':      float(parts[4]),
                'lon':      float(parts[5]),
                'alt_ft':   int(parts[6]),
                'gs_kts':   int(parts[7]),
            }
            if self.cb.on_pilot_pos:
                self.cb.on_pilot_pos(d)
        except Exception:
            pass
