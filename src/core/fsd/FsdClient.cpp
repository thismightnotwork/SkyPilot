#include "FsdClient.h"
#include "FsdParser.h"
#include <QDebug>

namespace SkyHigh::Fsd {
FsdClient::FsdClient(QObject* parent) : QObject(parent) {
    connect(&m_socket, &QTcpSocket::connected,    this, &FsdClient::onConnected);
    connect(&m_socket, &QTcpSocket::disconnected, this, &FsdClient::onDisconnected);
    connect(&m_socket, &QTcpSocket::readyRead,    this, &FsdClient::onReadyRead);
    connect(&m_socket, &QAbstractSocket::errorOccurred, this, &FsdClient::onErrorOccurred);
}
void FsdClient::connectToServer(const QString& host, quint16 port) {
    m_state = ConnectionState::Connecting;
    emit stateChanged(m_state);
    emit statusMessage(QString("Connecting to %1:%2").arg(host).arg(port));
    m_socket.connectToHost(host, port);
}
void FsdClient::disconnectFromServer() {
    m_socket.disconnectFromHost();
}
void FsdClient::beginLogin(const ConnectRequest& request) {
    m_pendingLogin = request;
    m_loginPending = true;
}
void FsdClient::sendTextMessage(const QString& to, const QString& message) {
    sendRaw(m_protocol.buildTextMessage(m_pendingLogin.callsign, to, message));
}
void FsdClient::sendPositionUpdate(const PositionReport& report) {
    sendRaw(m_protocol.buildPilotPosition(report));
}
void FsdClient::onConnected() {
    m_state = ConnectionState::Connected;
    emit stateChanged(m_state);
    emit statusMessage("Connected — authenticating");
    if (m_loginPending) {
        sendRaw(m_protocol.buildAddPilot(m_pendingLogin));
        m_loginPending = false;
    }
}
void FsdClient::onDisconnected() {
    m_state = ConnectionState::Disconnected;
    emit stateChanged(m_state);
    emit statusMessage("Disconnected");
}
void FsdClient::onReadyRead() {
    while (m_socket.canReadLine()) {
        const QString line = QString::fromLatin1(m_socket.readLine()).trimmed();
        if (line.isEmpty()) continue;
        const ParsedPacket packet = FsdParser::parse(line);
        emit packetReceived(packet);
    }
}
void FsdClient::onErrorOccurred(QAbstractSocket::SocketError error) {
    emit statusMessage(QString("Socket error: %1").arg(m_socket.errorString()));
    m_state = ConnectionState::Disconnected;
    emit stateChanged(m_state);
}
void FsdClient::sendRaw(const QString& line) {
    m_socket.write((line + "\r\n").toLatin1());
}
ConnectionState FsdClient::connectionState() const { return m_state; }
}
