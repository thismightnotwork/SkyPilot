import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
ApplicationWindow {
    visible: true
    width: 460; height: 700; minimumWidth: 420; minimumHeight: 640
    title: "SkyHigh Pilot"; color: "#1a1d23"
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 16; spacing: 12
        // ─ Connection Panel ───────────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 190; color: "#22262e"; radius: 8; border.color: "#2e3340"
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 12; spacing: 8
                Text { text: "SkyHigh Pilot"; color: "#e8eaf0"; font.pixelSize: 22; font.bold: true }
                RowLayout {
                    Layout.fillWidth: true
                    TextField { Layout.fillWidth: true; placeholderText: "Callsign"; text: connectionViewModel.callsign; onTextChanged: connectionViewModel.callsign = text; background: Rectangle { color: "#1a1d23"; radius: 4 }; color: "#e8eaf0" }
                    TextField { Layout.fillWidth: true; placeholderText: "Aircraft ICAO"; text: "A20N"; background: Rectangle { color: "#1a1d23"; radius: 4 }; color: "#e8eaf0" }
                }
                RowLayout {
                    Layout.fillWidth: true
                    TextField { Layout.fillWidth: true; placeholderText: "CID / VATSIM ID"; text: connectionViewModel.cid; onTextChanged: connectionViewModel.cid = text; background: Rectangle { color: "#1a1d23"; radius: 4 }; color: "#e8eaf0" }
                    TextField { Layout.fillWidth: true; placeholderText: "Password"; echoMode: TextInput.Password; text: connectionViewModel.password; onTextChanged: connectionViewModel.password = text; background: Rectangle { color: "#1a1d23"; radius: 4 }; color: "#e8eaf0" }
                }
                Text { text: "Server: fsd.YOUR-DOMAIN.com  |  Voice: voice.YOUR-DOMAIN.com"; color: "#8892a4"; font.pixelSize: 11 }
                Button {
                    text: connectionViewModel.connected ? "DISCONNECT" : "CONNECT"
                    onClicked: connectionViewModel.connectOrDisconnect()
                    background: Rectangle { color: connectionViewModel.connected ? "#c0392b" : "#2980b9"; radius: 4 }
                    contentItem: Text { text: parent.text; color: "#ffffff"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }
            }
        }
        // ─ Messages Panel ───────────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true; color: "#22262e"; radius: 8; border.color: "#2e3340"
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 12; spacing: 8
                RowLayout {
                    Text { text: "MESSAGES"; color: "#e8eaf0"; font.bold: true }
                    Rectangle { width: 20; height: 20; radius: 10; color: "#e74c3c"; visible: connectionViewModel.unreadMessages > 0
                        Text { anchors.centerIn: parent; text: connectionViewModel.unreadMessages; color: "#fff"; font.pixelSize: 11 }
                    }
                }
                ListView {
                    Layout.fillWidth: true; Layout.fillHeight: true; model: connectionViewModel.messagesModel; clip: true
                    delegate: Rectangle {
                        width: ListView.view.width; height: 40; color: "transparent"
                        RowLayout {
                            anchors.fill: parent; anchors.leftMargin: 4
                            Text { text: channel; color: "#2980b9"; font.pixelSize: 11; font.bold: true }
                            Text { text: from + ":"; color: "#e8eaf0"; font.bold: true; Layout.preferredWidth: 80; elide: Text.ElideRight }
                            Text { text: model.text; color: unread ? "#e8eaf0" : "#8892a4"; Layout.fillWidth: true; elide: Text.ElideRight }
                            Text { text: timestamp.substring(11,19); color: "#555e6e"; font.pixelSize: 11 }
                        }
                    }
                }
            }
        }
        // ─ Traffic Panel ────────────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true; color: "#22262e"; radius: 8; border.color: "#2e3340"
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 12; spacing: 8
                Text { text: "NEARBY TRAFFIC  (" + connectionViewModel.trafficCount + ")"; color: "#e8eaf0"; font.bold: true }
                ListView {
                    Layout.fillWidth: true; Layout.fillHeight: true; model: connectionViewModel.trafficModel; clip: true
                    delegate: Rectangle {
                        width: ListView.view.width; height: 36; color: "transparent"
                        border.color: "#2e3340"; border.width: index > 0 ? 0 : 0
                        RowLayout {
                            anchors.fill: parent; anchors.leftMargin: 4
                            Text { text: callsign; color: "#4caf50"; font.bold: true; Layout.preferredWidth: 80 }
                            Text { text: "FL" + Math.round(altitudeFeet / 100); color: "#e8eaf0"; Layout.preferredWidth: 55 }
                            Text { text: "HDG " + headingDegrees + "°"; color: "#e8eaf0"; Layout.preferredWidth: 70 }
                            Text { text: "GS " + groundspeed + "kt"; color: "#e8eaf0"; Layout.fillWidth: true }
                        }
                    }
                }
            }
        }
        // ─ Status Bar ─────────────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true; height: 36; color: "#22262e"; radius: 8; border.color: "#2e3340"
            RowLayout {
                anchors.fill: parent; anchors.margins: 10
                Rectangle { width: 10; height: 10; radius: 5; color: connectionViewModel.connected ? "#4caf50" : "#e74c3c" }
                Text { text: connectionViewModel.status.length > 0 ? connectionViewModel.status : "Idle — not connected"; color: connectionViewModel.connected ? "#4caf50" : "#8892a4" }
            }
        }
    }
}
