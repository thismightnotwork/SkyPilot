from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from audio.mumble_radio import MumbleRadioClient
from audio.ptt import PTTController
from network.fsd_client import FSDClient, FSDConfig
from sim.aircraft_state import AircraftState
from sim.simconnect_bridge import SimConnectBridge


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SkyPilot")
        self.resize(980, 640)

        self.state = AircraftState(callsign="SKY001")
        self.sim = SimConnectBridge(self.state)
        self.fsd = FSDClient(
            FSDConfig(
                callsign=self.state.callsign,
                real_name="SkyPilot User",
                server="127.0.0.1",
                port=6809,
            ),
            self.state,
        )
        self.radio = MumbleRadioClient(self.state)
        self.ptt = PTTController(self.state)

        self._build_ui()
        self._apply_style()

        self.sim.start()
        self.radio.start()
        self.ptt.start()
        self.fsd.connect()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(250)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.timer.stop()
        self.ptt.stop()
        self.radio.stop()
        self.fsd.disconnect()
        self.sim.stop()
        super().closeEvent(event)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("SkyPilot Development Client")
        title.setObjectName("title")
        self.status_label = QLabel("Offline FSD fallback")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.status_label)
        root.addLayout(header)

        grid = QGridLayout()
        root.addLayout(grid)

        self.telemetry = self._info_box("Telemetry")
        self.com1_box = self._radio_box("COM1", 1)
        self.com2_box = self._radio_box("COM2", 2)

        grid.addWidget(self.telemetry["box"], 0, 0)
        grid.addWidget(self.com1_box["box"], 0, 1)
        grid.addWidget(self.com2_box["box"], 0, 2)

        stations_box = QGroupBox("Visible stations")
        stations_layout = QVBoxLayout(stations_box)
        self.station_table = QTableWidget(0, 4)
        self.station_table.setHorizontalHeaderLabels(["Callsign", "Frequency", "Distance NM", "Quality"])
        stations_layout.addWidget(self.station_table)
        root.addWidget(stations_box)

    def _info_box(self, title: str) -> dict:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        labels = {}
        for key in ("Latitude", "Longitude", "Altitude ft", "Heading", "GS kts", "VS fpm", "Squawk"):
            lbl = QLabel(f"{key}: --")
            labels[key] = lbl
            layout.addWidget(lbl)
        labels["box"] = box
        return labels

    def _radio_box(self, title: str, index: int) -> dict:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        active = QLabel("Active: --")
        standby = QLabel("Standby: --")
        tx = QLabel("TX: idle")
        button = QPushButton("Swap")
        button.clicked.connect(lambda: self.state.swap_com(index))
        layout.addWidget(active)
        layout.addWidget(standby)
        layout.addWidget(tx)
        layout.addWidget(button)
        return {"box": box, "active": active, "standby": standby, "tx": tx}

    def _tick(self) -> None:
        self.fsd.send_position_update()
        self.radio.update()

        self.telemetry["Latitude"].setText(f"Latitude: {self.state.latitude_deg:.5f}")
        self.telemetry["Longitude"].setText(f"Longitude: {self.state.longitude_deg:.5f}")
        self.telemetry["Altitude ft"].setText(f"Altitude ft: {self.state.altitude_ft:.0f}")
        self.telemetry["Heading"].setText(f"Heading: {self.state.heading_deg:.1f}")
        self.telemetry["GS kts"].setText(f"GS kts: {self.state.groundspeed_kts:.0f}")
        self.telemetry["VS fpm"].setText(f"VS fpm: {self.state.vertical_speed_fpm:.0f}")
        self.telemetry["Squawk"].setText(f"Squawk: {self.state.transponder_code}")

        for box, radio in ((self.com1_box, self.state.radios.com1), (self.com2_box, self.state.radios.com2)):
            box["active"].setText(f"Active: {radio.active_mhz:.3f}")
            box["standby"].setText(f"Standby: {radio.standby_mhz:.3f}")
            box["tx"].setText(f"TX: {'LIVE' if radio.ptt else 'idle'}")

        self.status_label.setText("FSD connected" if self.fsd.connected else "Offline FSD fallback")

        stations = self.radio.visible_stations()
        self.station_table.setRowCount(len(stations))
        for row, station in enumerate(stations):
            self.station_table.setItem(row, 0, QTableWidgetItem(station["callsign"]))
            self.station_table.setItem(row, 1, QTableWidgetItem(f"{station['frequency']:.3f}"))
            self.station_table.setItem(row, 2, QTableWidgetItem(f"{station['distance_nm']:.1f}"))
            self.station_table.setItem(row, 3, QTableWidgetItem(f"{station['quality'] * 100:.0f}%"))

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background: #11161c; color: #d7e0ea; font-size: 14px; }
            QGroupBox { border: 1px solid #2b3744; margin-top: 10px; padding-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QPushButton { background: #1d6fa5; border: none; padding: 8px 12px; border-radius: 4px; }
            QPushButton:hover { background: #2486c5; }
            QTableWidget { background: #0d1217; gridline-color: #2b3744; }
            QLabel#title { font-size: 24px; font-weight: 700; }
            """
        )


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
