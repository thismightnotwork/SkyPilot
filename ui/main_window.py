from __future__ import annotations
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QStatusBar, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class RadioStateWidget(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Radio")
        layout = QFormLayout()
        self.com1_active = QLabel("---")
        self.com1_standby = QLabel("---")
        self.ptt_label = QLabel("PTT: OFF")
        self.ptt_label.setStyleSheet("color: grey; font-weight: bold;")
        layout.addRow("COM1 Active:", self.com1_active)
        layout.addRow("COM1 Standby:", self.com1_standby)
        layout.addRow("", self.ptt_label)
        self.setLayout(layout)

    def update_radio(self, active: float, standby: float, ptt: bool) -> None:
        self.com1_active.setText(f"{active:.3f} MHz")
        self.com1_standby.setText(f"{standby:.3f} MHz")
        self.ptt_label.setText("PTT: TRANSMITTING" if ptt else "PTT: OFF")
        self.ptt_label.setStyleSheet(
            "color: red; font-weight: bold;" if ptt else "color: grey; font-weight: bold;"
        )


class PositionWidget(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Position")
        layout = QFormLayout()
        self.lat = QLabel("---")
        self.lon = QLabel("---")
        self.alt = QLabel("---")
        self.hdg = QLabel("---")
        self.gs = QLabel("---")
        layout.addRow("Latitude:", self.lat)
        layout.addRow("Longitude:", self.lon)
        layout.addRow("Altitude:", self.alt)
        layout.addRow("Heading:", self.hdg)
        layout.addRow("GS:", self.gs)
        self.setLayout(layout)

    def update_position(self, lat, lon, alt, hdg, gs) -> None:
        self.lat.setText(f"{lat:.5f}\u00b0")
        self.lon.setText(f"{lon:.5f}\u00b0")
        self.alt.setText(f"{alt:,.0f} ft")
        self.hdg.setText(f"{hdg:.1f}\u00b0")
        self.gs.setText(f"{gs:.0f} kts")


class ConnectionWidget(QGroupBox):
    connect_requested = Signal(str, int, str, str, str, str)
    disconnect_requested = Signal()

    def __init__(self) -> None:
        super().__init__("Connection")
        layout = QFormLayout()
        self.server = QLineEdit("fsd.skyhigh.aero")
        self.port = QLineEdit("6809")
        self.callsign = QLineEdit()
        self.cid = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.name = QLineEdit()
        layout.addRow("Server:", self.server)
        layout.addRow("Port:", self.port)
        layout.addRow("Callsign:", self.callsign)
        layout.addRow("CID:", self.cid)
        layout.addRow("Password:", self.password)
        layout.addRow("Name:", self.name)
        btn_row = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setEnabled(False)
        btn_row.addWidget(self.connect_btn)
        btn_row.addWidget(self.disconnect_btn)
        layout.addRow(btn_row)
        self.setLayout(layout)
        self.connect_btn.clicked.connect(self._on_connect)
        self.disconnect_btn.clicked.connect(self.disconnect_requested)

    def _on_connect(self) -> None:
        self.connect_requested.emit(
            self.server.text(), int(self.port.text()),
            self.callsign.text(), self.cid.text(),
            self.password.text(), self.name.text()
        )

    def set_connected(self, connected: bool) -> None:
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SkyPilot \u2014 SkyHigh Network")
        self.setMinimumWidth(500)
        central = QWidget()
        root = QVBoxLayout(central)
        root.setSpacing(8)

        self.conn_widget = ConnectionWidget()
        self.radio_widget = RadioStateWidget()
        self.pos_widget = PositionWidget()

        root.addWidget(self.conn_widget)
        row = QHBoxLayout()
        row.addWidget(self.radio_widget)
        row.addWidget(self.pos_widget)
        root.addLayout(row)

        self.setCentralWidget(central)
        status = QStatusBar()
        self.setStatusBar(status)
        self.status_label = QLabel("Not connected")
        status.addWidget(self.status_label)

    def set_status(self, msg: str) -> None:
        self.status_label.setText(msg)
