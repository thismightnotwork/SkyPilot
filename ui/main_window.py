from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

DARK = """
QWidget {
    background: #1c1f26;
    color: #e8edf5;
    font-family: 'Segoe UI';
    font-size: 10pt;
}
QMainWindow { background: #1c1f26; }
QGroupBox {
    border: 1px solid #313744;
    border-radius: 8px;
    margin-top: 12px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
    color: #d9e1ee;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #93a4bd;
}
QLineEdit {
    background: #12151b;
    border: 1px solid #343b49;
    border-radius: 6px;
    padding: 7px 8px;
    color: #f4f7fb;
}
QLineEdit:focus { border: 1px solid #4fa3ff; }
QPushButton {
    background: #2b6de5;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover { background: #3a7bf0; }
QPushButton:pressed { background: #1f55c0; }
QPushButton:disabled { background: #38404e; color: #9aa6b8; }
QPushButton[secondary='true'] {
    background: #2b313d;
    color: #d8e0eb;
    border: 1px solid #3b4352;
}
QPushButton[secondary='true']:hover { background: #353d4a; }
QFrame#stationCard {
    background: #232833;
    border: 1px solid #313744;
    border-radius: 8px;
}
QLabel[caption='true'] { color: #8f9eb3; font-size: 9pt; }
QLabel[freq='true'] { color: #f5f8fd; font-size: 20pt; font-weight: 700; letter-spacing: 1px; }
QLabel[ok='true']   { color: #5fd38d; font-weight: 700; }
QLabel[warn='true'] { color: #ff6b6b; font-weight: 700; }
QLabel[idle='true'] { color: #8f9eb3; }
QStatusBar { background: #12151b; color: #aab5c5; font-size: 9pt; border-top: 1px solid #2a2f3a; }
"""


class FreqField(QWidget):
    """Large frequency display with label above, like xPilot's COM boxes."""

    def __init__(self, label: str, value: str = '121.800'):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.caption = QLabel(label)
        self.caption.setProperty('caption', True)
        self.display = QLabel(value)
        self.display.setProperty('freq', True)
        layout.addWidget(self.caption)
        layout.addWidget(self.display)

    def set(self, mhz: float):
        self.display.setText(f'{mhz:.3f}')


class SmallField(QWidget):
    """Compact label+value pair for telemetry data."""

    def __init__(self, label: str, value: str = '---'):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        cap = QLabel(label)
        cap.setProperty('caption', True)
        self.val = QLabel(value)
        self.val.setStyleSheet('font-weight: 600; font-size: 11pt;')
        layout.addWidget(cap)
        layout.addWidget(self.val)

    def set(self, text: str):
        self.val.setText(text)


class RadioPanel(QGroupBox):
    swap_requested = Signal()

    def __init__(self):
        super().__init__('Radio')
        root = QVBoxLayout(self)
        root.setSpacing(10)

        # COM1 row
        freq_row = QHBoxLayout()
        self.com1_active = FreqField('COM1 Active', '121.800')
        swap_col = QVBoxLayout()
        swap_col.setAlignment(Qt.AlignVCenter)
        self.swap_btn = QPushButton('\u21c4')
        self.swap_btn.setProperty('secondary', True)
        self.swap_btn.setFixedWidth(44)
        self.swap_btn.setToolTip('Swap active / standby')
        swap_col.addWidget(self.swap_btn)
        self.com1_standby = FreqField('COM1 Standby', '121.500')
        freq_row.addWidget(self.com1_active, 2)
        freq_row.addLayout(swap_col)
        freq_row.addWidget(self.com1_standby, 2)
        root.addLayout(freq_row)

        # TX / RX badges
        badge_row = QHBoxLayout()
        self.tx_badge = QLabel('TX')
        self.tx_badge.setProperty('warn', True)
        self.rx_badge = QLabel('RX READY')
        self.rx_badge.setProperty('ok', True)
        self.ptt_hint = QLabel('PTT: SPACE')
        self.ptt_hint.setProperty('caption', True)
        badge_row.addWidget(self.tx_badge)
        badge_row.addWidget(self.rx_badge)
        badge_row.addStretch(1)
        badge_row.addWidget(self.ptt_hint)
        root.addLayout(badge_row)

        self.swap_btn.clicked.connect(self.swap_requested)

    def update_radio(self, active: float, standby: float, ptt: bool):
        self.com1_active.set(active)
        self.com1_standby.set(standby)
        if ptt:
            self.tx_badge.setText('TX LIVE')
            self.tx_badge.setProperty('ok', True)
            self.tx_badge.setProperty('warn', False)
        else:
            self.tx_badge.setText('TX')
            self.tx_badge.setProperty('ok', False)
            self.tx_badge.setProperty('warn', True)
        self.tx_badge.style().unpolish(self.tx_badge)
        self.tx_badge.style().polish(self.tx_badge)


class TelemetryPanel(QGroupBox):
    def __init__(self):
        super().__init__('Aircraft')
        grid = QGridLayout(self)
        grid.setSpacing(12)
        self.lat = SmallField('Latitude')
        self.lon = SmallField('Longitude')
        self.alt = SmallField('Altitude')
        self.hdg = SmallField('Heading')
        self.gs  = SmallField('Groundspeed')
        self.sim = SmallField('Simulator', 'MSFS 2020/2024')
        for i, w in enumerate([self.lat, self.lon, self.alt, self.hdg, self.gs, self.sim]):
            grid.addWidget(w, i // 3, i % 3)

    def update_position(self, state):
        self.lat.set(f'{state.lat:.5f}\N{DEGREE SIGN}')
        self.lon.set(f'{state.lon:.5f}\N{DEGREE SIGN}')
        self.alt.set(f'{state.alt_ft:,.0f} ft')
        self.hdg.set(f'{state.heading_deg:.0f}\N{DEGREE SIGN}')
        self.gs.set(f'{state.groundspeed_kts:.0f} kt')


class StationCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName('stationCard')
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 8, 12, 8)
        self.name = QLabel('---')
        self.name.setStyleSheet('font-weight: 600;')
        self.freq = QLabel('---')
        self.freq.setProperty('caption', True)
        self.status = QLabel('')
        self.status.setProperty('idle', True)
        row.addWidget(self.name, 3)
        row.addWidget(self.freq, 2)
        row.addWidget(self.status, 2)

    def update(self, callsign: str, freq_mhz: float, status: str):
        self.name.setText(callsign)
        self.freq.setText(f'{freq_mhz:.3f} MHz')
        self.status.setText(status)
        ok = status in ('RX', 'ok')
        self.status.setProperty('ok', ok)
        self.status.setProperty('warn', not ok and callsign != '---')
        self.status.setProperty('idle', callsign == '---')
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)


class StationsPanel(QGroupBox):
    def __init__(self):
        super().__init__('Stations')
        root = QVBoxLayout(self)
        root.setSpacing(6)
        self.cards = [StationCard() for _ in range(5)]
        for c in self.cards:
            root.addWidget(c)
        root.addStretch(1)

    def update_rows(self, rows: list):
        for i, card in enumerate(self.cards):
            if i < len(rows):
                r = rows[i]
                card.update(r['callsign'], r['freq'], r['status'])
            else:
                card.update('---', 0.0, '')


class ConnectionPanel(QGroupBox):
    connect_requested = Signal(str, int, str, str, str, str, str, int)
    disconnect_requested = Signal()

    def __init__(self):
        super().__init__('Network')
        root = QVBoxLayout(self)
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        self.server        = QLineEdit('fsd.skyhigh.aero')
        self.port          = QLineEdit('6809')
        self.mumble_server = QLineEdit('voice.skyhigh.aero')
        self.mumble_port   = QLineEdit('64738')
        self.callsign      = QLineEdit('SH001')
        self.cid           = QLineEdit('1000000')
        self.password      = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.name          = QLineEdit('Pilot')

        fields = [
            ('FSD Server', self.server),     ('FSD Port',    self.port),
            ('Voice Server', self.mumble_server), ('Voice Port', self.mumble_port),
            ('Callsign',   self.callsign),   ('CID',         self.cid),
            ('Password',   self.password),   ('Name',        self.name),
        ]
        for i, (label, widget) in enumerate(fields):
            cap = QLabel(label)
            cap.setProperty('caption', True)
            row, col = divmod(i, 2)
            grid.addWidget(cap,    row * 2,     col)
            grid.addWidget(widget, row * 2 + 1, col)

        btn_row = QHBoxLayout()
        self.connect_btn    = QPushButton('Connect')
        self.disconnect_btn = QPushButton('Disconnect')
        self.disconnect_btn.setProperty('secondary', True)
        self.disconnect_btn.setEnabled(False)
        btn_row.addWidget(self.connect_btn)
        btn_row.addWidget(self.disconnect_btn)
        btn_row.addStretch(1)

        root.addLayout(grid)
        root.addLayout(btn_row)

        self.connect_btn.clicked.connect(self._emit_connect)
        self.disconnect_btn.clicked.connect(self.disconnect_requested)

    def _emit_connect(self):
        try:
            port = int(self.port.text())
        except ValueError:
            port = 6809
        try:
            mport = int(self.mumble_port.text())
        except ValueError:
            mport = 64738
        self.connect_requested.emit(
            self.server.text().strip(), port,
            self.callsign.text().strip(), self.cid.text().strip(),
            self.password.text(), self.name.text().strip(),
            self.mumble_server.text().strip(), mport,
        )

    def set_connected(self, value: bool):
        self.connect_btn.setEnabled(not value)
        self.disconnect_btn.setEnabled(value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SkyPilot')
        self.resize(1060, 680)
        self.setStyleSheet(DARK)
        self._build()

    def _build(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 14)
        root.setSpacing(10)

        # ── Title bar ────────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title = QLabel('SkyPilot')
        f = QFont('Segoe UI', 20)
        f.setBold(True)
        title.setFont(f)
        sub = QLabel('SkyHigh Network pilot client')
        sub.setProperty('caption', True)
        stack = QVBoxLayout()
        stack.setSpacing(0)
        stack.addWidget(title)
        stack.addWidget(sub)
        title_row.addLayout(stack)
        title_row.addStretch(1)
        self.badge = QLabel('Disconnected')
        self.badge.setProperty('warn', True)
        title_row.addWidget(self.badge)
        root.addLayout(title_row)

        # ── Panels ───────────────────────────────────────────────────────────
        self.conn      = ConnectionPanel()
        self.radio     = RadioPanel()
        self.telemetry = TelemetryPanel()
        self.stations  = StationsPanel()

        root.addWidget(self.conn)

        middle = QHBoxLayout()
        middle.setSpacing(10)
        left = QVBoxLayout()
        left.setSpacing(10)
        left.addWidget(self.radio)
        left.addWidget(self.telemetry)
        middle.addLayout(left, 3)
        middle.addWidget(self.stations, 2)
        root.addLayout(middle)

        self.setCentralWidget(central)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('Ready — not connected')

    def set_connected(self, connected: bool):
        self.conn.set_connected(connected)
        self.badge.setText('Connected' if connected else 'Disconnected')
        self.badge.setProperty('ok',   connected)
        self.badge.setProperty('warn', not connected)
        self.badge.style().unpolish(self.badge)
        self.badge.style().polish(self.badge)
