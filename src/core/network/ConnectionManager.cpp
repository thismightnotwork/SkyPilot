#include "ConnectionManager.h"
#include "app/Config.h"

namespace SkyHigh {
ConnectionManager::ConnectionManager(QObject* parent) : QObject(parent) {
    connect(&m_fsdClient, &Fsd::FsdClient::statusMessage, this, [this](const QString& message) { m_status = message; emit statusChanged(); });
    connect(&m_fsdClient, &Fsd::FsdClient::stateChanged, this, [this](Fsd::ConnectionState state) {
        const bool nowConnected = state == Fsd::ConnectionState::Connected;
        if (m_connected != nowConnected) { m_connected = nowConnected; emit connectedChanged(); }
    });
    connect(&m_fsdClient, &Fsd::FsdClient::packetReceived, this, [this](const Fsd::ParsedPacket& packet) {
        switch (packet.type) {
            case Fsd::PacketType::TextMessage: m_messages.appendTextMessage(Fsd::toTextMessage(packet)); emit unreadMessagesChanged(); break;
            case Fsd::PacketType::Selcal: {
                const QString from = packet.fields.size() > 1 ? packet.fields.at(1) : QStringLiteral("ATC");
                const QString code = packet.fields.size() > 2 ? packet.fields.at(2) : QStringLiteral("AB-CD");
                m_messages.appendSelcal(from, code); emit unreadMessagesChanged(); break;
            }
            case Fsd::PacketType::Position: m_traffic.upsertFromPositionPacket(Fsd::toPositionPacket(packet)); emit trafficCountChanged(); break;
            case Fsd::PacketType::DeleteClient: if (packet.fields.size() > 1) { m_traffic.removeByCallsign(packet.fields.at(1)); emit trafficCountChanged(); } break;
            default: break;
        }
    });
}
QString ConnectionManager::status() const { return m_status; }
bool ConnectionManager::connected() const { return m_connected; }
QObject* ConnectionManager::messagesModel() { return &m_messages; }
QObject* ConnectionManager::trafficModel() { return &m_traffic; }
int ConnectionManager::unreadMessages() const { return m_messages.unreadCount(); }
int ConnectionManager::trafficCount() const { return m_traffic.aircraftCount(); }
void ConnectionManager::connectPilot(const QString& callsign, const QString& cid, const QString& password) {
    Fsd::ConnectRequest request; request.callsign = callsign; request.cid = cid; request.password = password; request.realName = callsign;
    m_fsdClient.beginLogin(request); m_fsdClient.connectToServer(SkyHigh::Config::FSD_SERVER_HOST, SkyHigh::Config::FSD_SERVER_PORT);
    m_status = QString("Connecting to %1:%2").arg(SkyHigh::Config::FSD_SERVER_HOST).arg(SkyHigh::Config::FSD_SERVER_PORT); emit statusChanged();
}
void ConnectionManager::disconnectPilot() { m_fsdClient.disconnectFromServer(); m_status = QStringLiteral("Disconnected"); emit statusChanged(); }
}
