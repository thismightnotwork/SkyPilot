#include "MumbleClient.h"
#include "app/Config.h"
namespace SkyHigh {
MumbleClient::MumbleClient(QObject* parent) : QObject(parent) {
    connect(&m_socket, &QTcpSocket::connected, this, [this]{ m_connected = true; emit connectedChanged(); });
    connect(&m_socket, &QTcpSocket::disconnected, this, [this]{ m_connected = false; emit connectedChanged(); });
}
bool MumbleClient::isConnected() const { return m_connected; }
bool MumbleClient::isTransmitting() const { return m_transmitting; }
void MumbleClient::connectToServer(const QString& host, quint16 port, const QString& username) {
    Q_UNUSED(username);
    m_socket.connectToHost(host, port);
}
void MumbleClient::disconnect() { m_socket.disconnectFromHost(); }
void MumbleClient::setPtt(bool active) { if (m_transmitting != active) { m_transmitting = active; emit transmittingChanged(); } }
}
