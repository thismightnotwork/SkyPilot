from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QStatusBar, QVBoxLayout, QWidget,
)

DARK_QSS = """
QWidget {
    background: #12151c;
    color: #dce5f4;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 10pt;
}
QMainWindow, QDialog { background: #12151c; }
QGroupBox {
    border: 1px solid #252c3a;
    border-radius: 8px;
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
    color: #c9d5e8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #7a90b0;
    font-size: 9pt;
}
QLineEdit {
    background: #0d1018;
    border: 1px solid #2a3244;
    border-radius: 6px;
    padding: 7px 9px;
    color: #eaf0fb;
}
QLineEdit:focus { border-color: #4fa3ff; }
QPushButton {
    background: #1e4fb8;
    color: #f0f5ff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}
QPushButton:hover   { background: #2860d4; }
QPushButton:pressed { background: #163a8c; }
QPushButton:disabled{ background: #1e2330; color: #4a5568; }
QPushButton[role='secondary'] {
    background: #1c2333;
    color: #c5d2e8;
    border: 1px solid #2a3448;
}
QPushButton[role='danger'] { background: #7a1c2a; color: #ffd0d8; }
QFrame#card {
    background: #181d28;
    border: 1px solid #252c3a;
    border-radius: 8px;
}
QLabel[role='caption']  { color: #5c738a; font-size: 9pt; }
QLabel[role='freq']     { color: #e8f2ff; font-size: 22pt; font-weight: 700; }
QLabel[role='tx-live']  { color: #5fd38d; font-weight: 700; font-size: 9pt; }
QLabel[role='tx-idle']  { color: #3d5272; font-weight: 700; font-size: 9pt; }
QLabel[role='rx-ok']    { color: #5fd38d; font-size: 9pt; }
QLabel[role='rx-warn']  { color: #ff7a6b; font-size: 9pt; }
QLabel[role='rx-idle']  { color: #3d5272; font-size: 9pt; }
QLabel[role='value']    { font-weight: 600; font-size: 11pt; color: #c8d8f0; }
QStatusBar {
    background: #0d1018;
    color: #4a6080;
    font-size: 9pt;
    border-top: 1px solid #1e2636;
}
"""

class _Caption(QLabel):
    def __init__(self, text: str):
        super().__init__(text.upper())
        self.setProperty('role', 'caption')

class _Value(QLabel):
    def __init__(self, text: str = '---'):
        super().__init__(text)
        self.setProperty('role', 'value')

class FreqDisplay(QWidget):
    def __init__(self, label: str, mhz: float = 121.800):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        self._cap  = _Caption(label)
        self._disp = QLabel(f'{mhz:.3f}')
        self._disp.setProperty('role', 'freq')
        lay.addWidget(self._cap)
        lay.addWidget(self._disp)
    def set_mhz(self, mhz: float):
        self._disp.setText(f'{mhz:.3f}')
    @property
    def value_mhz(self) -> float:
        try:
            return float(self._disp.text())
        except ValueError:
            return 121.800

class TelemetryField(QWidget):
    def __init__(self, label: str, value: str = '---'):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(1)
        self._cap = _Caption(label)
        self._val = _Value(value)
        lay.addWidget(self._cap)
        lay.addWidget(self._val)
    def set(self, text: str):
        self._val.setText(text)

class RadioPanel(QGroupBox):
    swap_com1_requested = Signal()
    swap_com2_requested = Signal()
    def __init__(self):
        super().__init__('Radio Stack')
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.addLayout(self._com_row('COM1', 'com1'))
        root.addLayout(self._com_row('COM2', 'com2'))
        hint = QHBoxLayout()
        self._ptt_hint = _Caption('PTT  COM1: SPACE   COM2: CTRL+SPACE')
        hint.addWidget(self._ptt_hint)
        hint.addStretch(1)
        root.addLayout(hint)
        self._swap_com1.clicked.connect(self.swap_com1_requested)
        self._swap_com2.clicked.connect(self.swap_com2_requested)
    def _com_row(self, name: str, attr: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        active  = FreqDisplay(f'{name} Active')
        swap    = QPushButton('\u21c4')
        swap.setProperty('role', 'secondary')
        swap.setFixedWidth(44)
        standby = FreqDisplay(f'{name} Standby')
        tx_badge = QLabel('TX'); tx_badge.setProperty('role', 'tx-idle')
        rx_badge = QLabel('RX'); rx_badge.setProperty('role', 'rx-idle')
        row.addWidget(active, 2); row.addWidget(swap); row.addWidget(standby, 2)
        row.addWidget(tx_badge); row.addWidget(rx_badge); row.addStretch(1)
        setattr(self, f'_active_{attr}', active)
        setattr(self, f'_standby_{attr}', standby)
        setattr(self, f'_swap_{attr}', swap)
        setattr(self, f'_tx_{attr}', tx_badge)
        setattr(self, f'_rx_{attr}', rx_badge)
        return row
    def update_com(self, com: int, active_mhz: float, standby_mhz: float, ptt: bool, has_rx: bool):
        a = f'com{com}'
        getattr(self, f'_active_{a}').set_mhz(active_mhz)
        getattr(self, f'_standby_{a}').set_mhz(standby_mhz)
        tx = getattr(self, f'_tx_{a}'); rx = getattr(self, f'_rx_{a}')
        tx.setText('TX LIVE' if ptt else 'TX')
        tx.setProperty('role', 'tx-live' if ptt else 'tx-idle')
        rx.setProperty('role', 'rx-ok' if has_rx else 'rx-idle')
        for lbl in (tx, rx):
            lbl.style().unpolish(lbl); lbl.style().polish(lbl)

class TelemetryPanel(QGroupBox):
    def __init__(self):
        super().__init__('Aircraft')
        grid = QGridLayout(self)
        grid.setSpacing(14)
        self.lat  = TelemetryField('Latitude')
        self.lon  = TelemetryField('Longitude')
        self.alt  = TelemetryField('Altitude')
        self.hdg  = TelemetryField('Heading')
        self.gs   = TelemetryField('Groundspeed')
        self.vs   = TelemetryField('Vert Speed')
        self.sqk  = TelemetryField('Squawk')
        self.sim  = TelemetryField('Simulator', 'MSFS 2020/2024')
        for i, w in enumerate([self.lat, self.lon, self.alt, self.hdg, self.gs, self.vs, self.sqk, self.sim]):
            grid.addWidget(w, i // 4, i % 4)
    def update(self, state):
        self.lat.set(f'{state.lat:.5f}°'); self.lon.set(f'{state.lon:.5f}°')
        self.alt.set(f'{state.alt_ft:,.0f} ft'); self.hdg.set(f'{state.heading_deg:.0f}°')
        self.gs.set(f'{state.groundspeed_kts:.0f} kt'); self.vs.set(f'{state.vertical_speed_fpm:+,.0f} fpm')
        self.sqk.set(state.squawk)

class StationRow(QFrame):
    def __init__(self):
        super().__init__(); self.setObjectName('card')
        row = QHBoxLayout(self); row.setContentsMargins(12, 8, 12, 8); row.setSpacing(10)
        self._cs = QLabel('---'); self._cs.setStyleSheet('font-weight: 600;')
        self._freq = _Caption('---'); self._dist = _Caption('---'); self._qual = _Caption('---')
        self._status = QLabel(''); self._status.setProperty('role', 'rx-idle')
        for w, stretch in [(self._cs, 3), (self._freq, 2), (self._dist, 2), (self._qual, 1), (self._status, 2)]:
            row.addWidget(w, stretch)
    def update(self, callsign: str, freq_mhz: float, status: str, dist_nm: float = 0, qual: float = 0):
        self._cs.setText(callsign); self._freq.setText(f'{freq_mhz:.3f} MHz')
        self._dist.setText(f'{dist_nm:.0f} nm' if callsign != '---' else '---')
        self._qual.setText(f'q={qual:.2f}' if callsign != '---' else '')
        self._status.setText(status)
        ok = status in ('RX', 'ok')
        self._status.setProperty('role', 'rx-ok' if ok else ('rx-warn' if callsign != '---' else 'rx-idle'))
        self._status.style().unpolish(self._status); self._status.style().polish(self._status)

class StationsPanel(QGroupBox):
    MAX_ROWS = 8
    def __init__(self):
        super().__init__('Stations')
        root = QVBoxLayout(self); root.setSpacing(4)
        hdr = QHBoxLayout()
        for txt, stretch in [('Callsign', 3), ('Freq', 2), ('Distance', 2), ('Q', 1), ('Status', 2)]:
            hdr.addWidget(_Caption(txt), stretch)
        root.addLayout(hdr)
        self._rows = [StationRow() for _ in range(self.MAX_ROWS)]
        for r in self._rows: root.addWidget(r)
        root.addStretch(1)
    def update_rows(self, rows: list):
        for i, row in enumerate(self._rows):
            if i < len(rows):
                r = rows[i]
                row.update(r.get('callsign', '---'), r.get('freq', 0.0), r.get('status', ''), r.get('dist_nm', 0), r.get('quality', 0))
            else:
                row.update('---', 0.0, '')

class ConnectionPanel(QGroupBox):
    connect_requested    = Signal(str, int, str, str, str, str, str, int)
    disconnect_requested = Signal()
    def __init__(self):
        super().__init__('Network')
        root = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(10); g.setVerticalSpacing(5)
        self.fsd_host    = QLineEdit('fsd.skyhigh.aero'); self.fsd_port = QLineEdit('6809')
        self.voice_host  = QLineEdit('voice.skyhigh.aero'); self.voice_port = QLineEdit('64738')
        self.callsign    = QLineEdit('SH001'); self.cid = QLineEdit('1000000')
        self.password    = QLineEdit(); self.password.setEchoMode(QLineEdit.Password)
        self.real_name   = QLineEdit('Pilot')
        fields = [
            ('FSD Server', self.fsd_host), ('FSD Port', self.fsd_port),
            ('Voice Server', self.voice_host), ('Voice Port', self.voice_port),
            ('Callsign', self.callsign), ('CID', self.cid),
            ('Password', self.password), ('Name', self.real_name),
        ]
        for i, (lbl_text, widget) in enumerate(fields):
            r, c = divmod(i, 2)
            g.addWidget(_Caption(lbl_text), r * 2, c)
            g.addWidget(widget, r * 2 + 1, c)
        root.addLayout(g)
        btn_row = QHBoxLayout()
        self._connect_btn = QPushButton('Connect')
        self._disconnect_btn = QPushButton('Disconnect'); self._disconnect_btn.setProperty('role', 'danger')
        self._disconnect_btn.setEnabled(False)
        btn_row.addWidget(self._connect_btn); btn_row.addWidget(self._disconnect_btn); btn_row.addStretch(1)
        root.addLayout(btn_row)
        self._connect_btn.clicked.connect(self._emit_connect)
        self._disconnect_btn.clicked.connect(self.disconnect_requested)
    def set_connected(self, connected: bool):
        self._connect_btn.setEnabled(not connected); self._disconnect_btn.setEnabled(connected)
    def _emit_connect(self):
        try: fsd_port = int(self.fsd_port.text())
        except: fsd_port = 6809
        try: voice_port = int(self.voice_port.text())
        except: voice_port = 64738
        self.connect_requested.emit(
            self.fsd_host.text().strip(), fsd_port,
            self.callsign.text().strip(), self.cid.text().strip(),
            self.password.text(), self.real_name.text().strip(),
            self.voice_host.text().strip(), voice_port,
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SkyPilot — SkyHigh Network')
        self.setMinimumSize(960, 640)
        self.setStyleSheet(DARK_QSS)
        central = QWidget(); self.setCentralWidget(central)
        root = QHBoxLayout(central); root.setContentsMargins(12, 12, 12, 12); root.setSpacing(12)
        left = QVBoxLayout(); left.setSpacing(10)
        self.conn = ConnectionPanel(); self.tele = TelemetryPanel()
        left.addWidget(self.conn); left.addWidget(self.tele); left.addStretch(1)
        right = QVBoxLayout(); right.setSpacing(10)
        self.radio = RadioPanel(); self.stations = StationsPanel()
        right.addWidget(self.radio); right.addWidget(self.stations, 1)
        root.addLayout(left, 4); root.addLayout(right, 6)
        self.statusbar = QStatusBar(); self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('SkyPilot ready — not connected')
    def set_connected(self, ok: bool):
        self.conn.set_connected(ok)
