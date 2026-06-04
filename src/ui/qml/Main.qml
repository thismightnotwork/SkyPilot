import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    width: 520; height: 800
    minimumWidth: 460; minimumHeight: 700
    title: "SkyHigh Pilot"
    color: "#1a1d23"

    // Tab bar at the top for main views
    header: TabBar {
        id: tabBar
        background: Rectangle { color: "#22262e" }
        TabButton { text: "CONNECTION"; font.pixelSize: 11; implicitHeight: 36 }
        TabButton { text: "MESSAGES";   font.pixelSize: 11; implicitHeight: 36 }
        TabButton { text: "MAP";        font.pixelSize: 11; implicitHeight: 36 }
        TabButton { text: "TRAFFIC";    font.pixelSize: 11; implicitHeight: 36 }
    }

    StackLayout {
        anchors.fill: parent
        anchors.margins: 10
        currentIndex: tabBar.currentIndex

        // ── Tab 0: CONNECTION ──────────────────────────────────────────────
        ColumnLayout {
            spacing: 10

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: connCol.implicitHeight + 24
                color: "#22262e"; radius: 8; border.color: "#2e3340"

                ColumnLayout {
                    id: connCol
                    anchors { left: parent.left; right: parent.right; top: parent.top; margins: 12 }
                    spacing: 8

                    RowLayout {
                        Text { text: "✈"; color: "#2980b9"; font.pixelSize: 22 }
                        Text { text: "SkyHigh Pilot"; color: "#e8eaf0"; font.pixelSize: 20; font.bold: true }
                        Item { Layout.fillWidth: true }
                        Text { text: "v1.0.0-alpha"; color: "#555e6e"; font.pixelSize: 11 }
                    }

                    RowLayout {
                        Layout.fillWidth: true; spacing: 8
                        SkyTextField { Layout.fillWidth: true; placeholderText: "Callsign";    text: connectionViewModel.callsign;  onTextChanged: connectionViewModel.callsign  = text }
                        SkyTextField { Layout.preferredWidth: 90; placeholderText: "ICAO type"; text: "A20N" }
                    }
                    RowLayout {
                        Layout.fillWidth: true; spacing: 8
                        SkyTextField { Layout.fillWidth: true; placeholderText: "CID / Pilot ID"; text: connectionViewModel.cid;      onTextChanged: connectionViewModel.cid      = text }
                        SkyTextField { Layout.fillWidth: true; placeholderText: "Password"; echoMode: TextInput.Password; text: connectionViewModel.password; onTextChanged: connectionViewModel.password = text }
                    }

                    // Server addresses
                    Column {
                        spacing: 2
                        Text { text: "FSD:   fsd.YOUR-DOMAIN.com:6809";   color: "#8892a4"; font.pixelSize: 11 }
                        Text { text: "Voice: voice.YOUR-DOMAIN.com:64738"; color: "#8892a4"; font.pixelSize: 11 }
                    }

                    // Sim selector
                    RowLayout {
                        spacing: 8
                        Text { text: "Simulator:"; color: "#8892a4"; font.pixelSize: 12 }
                        ComboBox {
                            model: ["MSFS 2020/2024", "X-Plane 11/12", "None"]
                            background: Rectangle { color: "#1a1d23"; radius: 4; border.color: "#2e3340" }
                            contentItem: Text { text: parent.displayText; color: "#e8eaf0"; font.pixelSize: 12; leftPadding: 6; verticalAlignment: Text.AlignVCenter }
                            onCurrentIndexChanged: connectionViewModel.setSimType(currentIndex)
                        }
                    }

                    Button {
                        Layout.fillWidth: true; implicitHeight: 36
                        text: connectionViewModel.connected ? "DISCONNECT" : "CONNECT"
                        onClicked: connectionViewModel.connectOrDisconnect()
                        background: Rectangle {
                            color: connectionViewModel.connected ? "#922b21" : "#1a5276"
                            radius: 5
                            Behavior on color { ColorAnimation { duration: 200 } }
                        }
                        contentItem: Text {
                            text: parent.text; color: "#ffffff"
                            horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
                            font.bold: true; font.pixelSize: 13
                        }
                    }
                }
            }

            // Sim status card
            Rectangle {
                Layout.fillWidth: true; implicitHeight: simCol.implicitHeight + 20
                color: "#22262e"; radius: 8; border.color: "#2e3340"
                ColumnLayout {
                    id: simCol
                    anchors { fill: parent; margins: 12 }; spacing: 6
                    Text { text: "SIMULATOR"; color: "#e8eaf0"; font.bold: true; font.pixelSize: 12 }
                    RowLayout {
                        spacing: 6
                        Rectangle { width:9;height:9;radius:5; color: connectionViewModel.simConnected ? "#4caf50" : "#e74c3c" }
                        Text { text: connectionViewModel.simStatus; color:"#8892a4"; font.pixelSize:12; Layout.fillWidth:true }
                    }
                    Text { text: connectionViewModel.ownPositionText; color:"#555e6e"; font.pixelSize:11; font.family:"Monospace" }
                }
            }

            Item { Layout.fillHeight: true }
        }

        // ── Tab 1: MESSAGES ────────────────────────────────────────────────
        ColumnLayout {
            spacing: 6

            RowLayout {
                Text { text: "MESSAGES"; color: "#e8eaf0"; font.bold: true; font.pixelSize: 13 }
                Rectangle {
                    visible: connectionViewModel.unreadMessages > 0
                    width: 20; height: 20; radius: 10; color: "#e74c3c"
                    Text { anchors.centerIn: parent; text: connectionViewModel.unreadMessages; color: "#fff"; font.pixelSize: 11 }
                }
            }

            ListView {
                Layout.fillWidth: true; Layout.fillHeight: true
                model: connectionViewModel.messagesModel
                clip: true
                ScrollBar.vertical: ScrollBar {}
                delegate: Rectangle {
                    width: ListView.view.width; height: 38
                    color: index % 2 === 0 ? "#1e2128" : "transparent"
                    RowLayout {
                        anchors { fill: parent; leftMargin: 6; rightMargin: 6 }; spacing: 6
                        Text { text: timestamp ? timestamp.substring(11,19) : ""; color:"#555e6e"; font.pixelSize:11; font.family:"Monospace" }
                        Text { text: "["+( channel||"?")+"]"; color:"#2980b9"; font.pixelSize:11; font.bold:true; Layout.preferredWidth:70; elide:Text.ElideRight }
                        Text { text: (from||"?")+":"; color:"#e8eaf0"; font.bold:true; Layout.preferredWidth:72; elide:Text.ElideRight }
                        Text { text: model.text||""; color: unread?"#e8eaf0":"#8892a4"; Layout.fillWidth:true; elide:Text.ElideRight }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true; spacing: 6
                SkyTextField {
                    id: composeField; Layout.fillWidth: true
                    placeholderText: "Type message — Enter to send to UNICOM"
                    Keys.onReturnPressed: { if (text.trim().length>0) { connectionViewModel.sendMessage("@94835", text.trim()); text="" } }
                }
                Button {
                    text:"Send"; implicitWidth:54; implicitHeight:30
                    onClicked: { if(composeField.text.trim().length>0){connectionViewModel.sendMessage("@94835",composeField.text.trim());composeField.text=""} }
                    background: Rectangle{color:"#1a5276";radius:4}
                    contentItem: Text{text:parent.text;color:"#fff";horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter}
                }
            }
        }

        // ── Tab 2: MAP ─────────────────────────────────────────────────────
        TrafficMap {
            trafficModel: connectionViewModel.trafficModel
            centerLat:    connectionViewModel.ownLat
            centerLon:    connectionViewModel.ownLon
        }

        // ── Tab 3: TRAFFIC LIST ────────────────────────────────────────────
        ColumnLayout {
            spacing: 6
            Text { text: "NEARBY TRAFFIC  (" + connectionViewModel.trafficCount + ")"; color:"#e8eaf0"; font.bold:true; font.pixelSize:13 }
            RowLayout {
                Layout.fillWidth: true
                Repeater {
                    model: ["CALLSIGN","TYPE","FL","HDG","GS","LAT","LON"]
                    Text { text:modelData; color:"#555e6e"; font.pixelSize:10; font.bold:true
                        Layout.preferredWidth: index===0?80:index===1?50:index<=3?50:60 }
                }
            }
            Rectangle { Layout.fillWidth:true; height:1; color:"#2e3340" }
            ListView {
                Layout.fillWidth:true; Layout.fillHeight:true
                model: connectionViewModel.trafficModel
                clip:true
                ScrollBar.vertical: ScrollBar{}
                delegate: Rectangle {
                    width:ListView.view.width; height:32
                    color: index%2===0?"#1e2128":"transparent"
                    RowLayout {
                        anchors{fill:parent;leftMargin:2}; spacing:0
                        Text{text:callsign;         color:"#4caf50";font.bold:true;font.pixelSize:12;Layout.preferredWidth:80}
                        Text{text:aircraftIcao||"?";color:"#2980b9";font.pixelSize:12;Layout.preferredWidth:50}
                        Text{text:"FL"+Math.round(altitudeFeet/100);color:"#e8eaf0";font.pixelSize:12;Layout.preferredWidth:50}
                        Text{text:headingDegrees+"°";color:"#e8eaf0";font.pixelSize:12;Layout.preferredWidth:50}
                        Text{text:groundspeed+"kt"; color:"#e8eaf0";font.pixelSize:12;Layout.preferredWidth:60}
                        Text{text:latitude?latitude.toFixed(4):"";  color:"#8892a4";font.pixelSize:11;Layout.preferredWidth:60}
                        Text{text:longitude?longitude.toFixed(4):"";color:"#8892a4";font.pixelSize:11;Layout.fillWidth:true}
                    }
                }
            }
        }
    }

    // ── Status Bar ─────────────────────────────────────────────────────────
    footer: Rectangle {
        height: 34; color: "#22262e"; border.color: "#2e3340"
        RowLayout {
            anchors{fill:parent;leftMargin:10;rightMargin:10}; spacing:8
            Rectangle{width:9;height:9;radius:5;color:connectionViewModel.connected?"#4caf50":"#e74c3c"}
            Text{text:"FSD";color:"#8892a4";font.pixelSize:11}
            Rectangle{width:1;height:16;color:"#2e3340"}
            Rectangle{width:9;height:9;radius:5;color:connectionViewModel.simConnected?"#4caf50":"#e74c3c"}
            Text{text:"SIM";color:"#8892a4";font.pixelSize:11}
            Rectangle{width:1;height:16;color:"#2e3340"}
            Rectangle{width:9;height:9;radius:5;color:"#e74c3c"}
            Text{text:"VOICE";color:"#8892a4";font.pixelSize:11}
            Item{Layout.fillWidth:true}
            Text{
                text: connectionViewModel.status.length>0 ? connectionViewModel.status : "Idle — not connected"
                color: connectionViewModel.connected ? "#4caf50" : "#8892a4"
                font.pixelSize:11; elide:Text.ElideRight; Layout.maximumWidth:280
            }
        }
    }

    // Reusable styled text field
    component SkyTextField: TextField {
        background: Rectangle{color:"#1a1d23";radius:4;border.color:"#2e3340"}
        color:"#e8eaf0"; placeholderTextColor:"#555e6e"; font.pixelSize:13; implicitHeight:30
    }
}
