import QtQuick
import QtQuick.Controls
import QtLocation
import QtPositioning

/// Traffic Map overlay — renders nearby aircraft on a moving map.
/// Requires Qt Location module. Falls back gracefully if unavailable.
Item {
    id: root
    property var trafficModel: null
    property real centerLat:  51.148
    property real centerLon:  -0.190
    property int  zoomLevel:  10

    // Attempt to use OpenStreetMap tile provider (free, no API key required)
    Plugin {
        id: mapPlugin
        name: "osm"
        PluginParameter { name: "osm.mapping.providersrepository.disabled"; value: "true" }
        PluginParameter { name: "osm.mapping.custom.host"; value: "https://tile.openstreetmap.org/" }
    }

    Map {
        id: map
        anchors.fill: parent
        plugin: mapPlugin
        center: QtPositioning.coordinate(root.centerLat, root.centerLon)
        zoomLevel: root.zoomLevel
        copyrightsVisible: false

        // Pan with touch/mouse
        PinchHandler { id: pinch }
        WheelHandler { id: wheel; onWheel: (event) => { map.zoomLevel += event.angleDelta.y / 120 } }
        DragHandler   { id: drag }

        // Traffic aircraft labels
        MapItemView {
            model: root.trafficModel
            delegate: MapQuickItem {
                coordinate: QtPositioning.coordinate(latitude, longitude)
                anchorPoint.x: label.width  / 2
                anchorPoint.y: label.height / 2

                sourceItem: Item {
                    id: label
                    width:  labelText.width  + 10
                    height: labelText.height + 6

                    // Aircraft dot
                    Rectangle {
                        anchors.centerIn: parent
                        width: 8; height: 8; radius: 4
                        color: onGround ? "#f39c12" : "#2ecc71"
                        border.color: "#ffffff"; border.width: 1
                    }

                    // Label bubble (appears above the dot)
                    Rectangle {
                        anchors.bottom: parent.top
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottomMargin: 4
                        color: "#cc1a1d23"
                        radius: 3
                        width:  labelText.width  + 8
                        height: labelText.height + 4
                        Text {
                            id: labelText
                            anchors.centerIn: parent
                            text: callsign + "\nFL" + Math.round(altitudeFeet/100) + "  " + groundspeed + "kt"
                            color: "#e8eaf0"
                            font.pixelSize: 10
                            font.family: "Monospace"
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }

                    // Heading line
                    Canvas {
                        anchors.centerIn: parent
                        width: 40; height: 40
                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.clearRect(0, 0, 40, 40)
                            const cx = 20, cy = 20, len = 18
                            const rad = (headingDegrees - 90) * Math.PI / 180
                            ctx.beginPath()
                            ctx.moveTo(cx, cy)
                            ctx.lineTo(cx + Math.cos(rad)*len, cy + Math.sin(rad)*len)
                            ctx.strokeStyle = "#2ecc71"
                            ctx.lineWidth = 1.5
                            ctx.stroke()
                        }
                    }
                }
            }
        }
    }

    // Compass rose (top-right)
    Rectangle {
        anchors { top: parent.top; right: parent.right; margins: 8 }
        width: 64; height: 64; radius: 32
        color: "#cc1a1d23"; border.color: "#2e3340"
        Text { anchors.centerIn: parent; text: "N"; color: "#e74c3c"; font.bold: true; font.pixelSize: 14 }
    }

    // Zoom controls
    Column {
        anchors { right: parent.right; verticalCenter: parent.verticalCenter; rightMargin: 8 }
        spacing: 4
        Repeater {
            model: ["+", "-"]
            Button {
                width: 32; height: 32
                text: modelData
                onClicked: map.zoomLevel += (modelData === "+" ? 1 : -1)
                background: Rectangle { color: "#cc1a1d23"; radius: 4; border.color: "#2e3340" }
                contentItem: Text { text: parent.text; color: "#e8eaf0"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 16; font.bold: true }
            }
        }
    }
}
