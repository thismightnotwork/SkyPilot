#include "ConnectionManager.h"
#include "app/Config.h"
#include <QDebug>

namespace SkyHigh {

ConnectionManager::ConnectionManager(QObject* parent) : QObject(parent) {
    connect(&m_fsdClient, &Fsd::FsdClient::statusMessage, this, [this](const QString& msg) {
        m_status = msg; emit statusChanged();
    });
    connect(&m_fsdClient, &Fsd::FsdClient::stateChanged, this, [this](Fsd::ConnectionState state) {
        const bool nowConnected = (state == Fsd::ConnectionState::Connected);
        if (m_connected != nowConnected) {
            m_connected = nowConnected;
            emit connectedChanged();
            if (m_connected) m_positionTimer.start();
            else             m_positionTimer.stop();
        }
    });
    connect(&m_fsdClient, &Fsd::FsdClient::packetReceived, this, [this](const Fsd::ParsedPacket& packet) {
        switch (packet.type) {
            case Fsd::PacketType::TextMessage:
                m_messages.appendTextMessage(Fsd::toTextMessage(packet));
                emit unreadMessagesChanged();
                break;
            case Fsd::PacketType::Selcal: {
                const QString from = packet.fields.size() > 1 ? packet.fields.at(1) : QStringLiteral("ATC");
                const QString code = packet.fields.size() > 2 ? packet.fields.at(2) : QStringLiteral("AB-CD");
                m_messages.appendSelcal(from, code);
                emit unreadMessagesChanged();
                break;
            }
            case Fsd::PacketType::Position:
                m_traffic.upsertFromPositionPacket(Fsd::toPositionPacket(packet));
                emit trafficCountChanged();
                break;
            case Fsd::PacketType::DeleteClient:
                if (packet.fields.size() > 1) {
                    m_traffic.removeByCallsign(packet.fields.at(1));
                    emit trafficCountChanged();
                }
                break;
            default: break;
        }
    });

    m_positionTimer.setInterval(5000);
    m_positionTimer.setSingleShot(false);
    connect(&m_positionTimer, &QTimer::timeout, this, &ConnectionManager::onPositionTimerTick);
}

QString  ConnectionManager::status()        const { return m_status; }
bool     ConnectionManager::connected()     const { return m_connected; }
QObject* ConnectionManager::messagesModel()       { return &m_messages; }
QObject* ConnectionManager::trafficModel()        { return &m_traffic; }
int      ConnectionManager::unreadMessages()const { return m_messages.unreadCount(); }
int      ConnectionManager::trafficCount()  const { return m_traffic.aircraftCount(); }

void ConnectionManager::connectPilot(const QString& callsign, const QString& cid, const QString& password) {
    Fsd::ConnectRequest req;
    req.callsign = callsign; req.cid = cid; req.password = password; req.realName = callsign;
    m_callsign = callsign;
    m_fsdClient.beginLogin(req);
    m_fsdClient.connectToServer(Config::FSD_SERVER_HOST, Config::FSD_SERVER_PORT);
    m_status = QString("Connecting to %1:%2…").arg(Config::FSD_SERVER_HOST).arg(Config::FSD_SERVER_PORT);
    emit statusChanged();
}

void ConnectionManager::disconnectPilot() {
    m_positionTimer.stop();
    m_fsdClient.disconnectFromServer();
    m_status = QStringLiteral("Disconnected");
    emit statusChanged();
}

void ConnectionManager::sendTextMessage(const QString& to, const QString& text) {
    m_fsdClient.sendTextMessage(to, text);
    // Echo outbound message into our own message list
    Fsd::TextMessagePacket echo;
    echo.from    = m_callsign;
    echo.to      = to;
    echo.message = text;
    m_messages.appendTextMessage(echo);
    emit unreadMessagesChanged();
}

void ConnectionManager::updateOwnPosition(double lat, double lon, int altFt, int hdg, int gs) {
    m_ownLat = lat; m_ownLon = lon; m_ownAlt = altFt; m_ownHdg = hdg;
    Q_UNUSED(gs);
}

void ConnectionManager::onPositionTimerTick() {
    Fsd::PositionReport report;
    report.callsign     = m_callsign;
    report.latitude     = m_ownLat;
    report.longitude    = m_ownLon;
    report.altitudeFeet = m_ownAlt;
    report.groundspeed  = 0;
    report.heading      = m_ownHdg;
    m_fsdClient.sendPositionUpdate(report);
}

} // namespace SkyHigh
