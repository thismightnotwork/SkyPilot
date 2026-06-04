#include "FsdClient.h"
#include "FsdParser.h"
#include <QDebug>

namespace SkyHigh::Fsd {

static constexpr int KEEPALIVE_INTERVAL_MS = 30000; // 30 s
static const int RECONNECT_DELAYS_MS[] = {3000, 10000, 30000}; // back-off steps
static constexpr int MAX_RECONNECT_ATTEMPTS = 3;

FsdClient::FsdClient(QObject* parent) : QObject(parent) {
    // Socket signals
    connect(&m_socket, &QTcpSocket::connected,    this, &FsdClient::onConnected);
    connect(&m_socket, &QTcpSocket::disconnected, this, &FsdClient::onDisconnected);
    connect(&m_socket, &QTcpSocket::readyRead,    this, &FsdClient::onReadyRead);
    connect(&m_socket, &QAbstractSocket::errorOccurred, this, &FsdClient::onErrorOccurred);

    // Keepalive — only active while connected
    m_keepaliveTimer.setInterval(KEEPALIVE_INTERVAL_MS);
    m_keepaliveTimer.setSingleShot(false);
    connect(&m_keepaliveTimer, &QTimer::timeout, this, &FsdClient::onKeepaliveTick);

    // Reconnect — single-shot, scheduled on error
    m_reconnectTimer.setSingleShot(true);
    connect(&m_reconnectTimer, &QTimer::timeout, this, [this]() {
        qDebug() << "[FSD] Reconnect attempt" << m_reconnectAttempts + 1;
        m_socket.connectToHost(m_lastHost, m_lastPort);
    });
}

void FsdClient::connectToServer(const QString& host, quint16 port) {
    m_lastHost = host;
    m_lastPort = port;
    m_reconnectAttempts = 0;
    m_serverIdentReceived = false;
    m_state = ConnectionState::Connecting;
    emit stateChanged(m_state);
    emit statusMessage(QString("Connecting to %1:%2 …").arg(host).arg(port));
    m_socket.connectToHost(host, port);
}

void FsdClient::disconnectFromServer() {
    m_reconnectTimer.stop();
    m_reconnectAttempts = MAX_RECONNECT_ATTEMPTS; // prevent auto-reconnect
    if (m_loginPending || m_state == ConnectionState::Connected) {
        sendRaw(m_protocol.buildDeletePilot(m_pendingLogin.callsign));
    }
    m_socket.disconnectFromHost();
}

void FsdClient::beginLogin(const ConnectRequest& request) {
    m_pendingLogin  = request;
    m_loginPending  = true;
}

void FsdClient::sendTextMessage(const QString& to, const QString& message) {
    if (m_state != ConnectionState::Connected) return;
    sendRaw(m_protocol.buildTextMessage(m_pendingLogin.callsign, to, message));
}

void FsdClient::sendPositionUpdate(const PositionReport& report) {
    if (m_state != ConnectionState::Connected) return;
    sendRaw(m_protocol.buildPilotPosition(report));
}

void FsdClient::sendFlightPlan(const FlightPlanData& fp) {
    if (m_state != ConnectionState::Connected) return;
    sendRaw(m_protocol.buildFlightPlan(m_pendingLogin.callsign, fp));
}

void FsdClient::onConnected() {
    m_reconnectAttempts = 0;
    m_serverIdentReceived = false;
    // Do NOT send #AP here — wait for the server to send $DI first.
    // Some FSD variants send $DI immediately; we handle it in handleServerIdent().
    // As a fallback, if no $DI arrives within 5 s, send #AP anyway.
    QTimer::singleShot(5000, this, [this]() {
        if (m_loginPending && !m_serverIdentReceived && m_state != ConnectionState::Disconnected) {
            qDebug() << "[FSD] No $DI received; sending #AP as fallback";
            sendRaw(m_protocol.buildAddPilot(m_pendingLogin));
            m_loginPending = false;
        }
    });
    m_keepaliveTimer.start();
    m_state = ConnectionState::Connected;
    emit stateChanged(m_state);
    emit statusMessage("TCP connected — awaiting server ident");
}

void FsdClient::onDisconnected() {
    m_keepaliveTimer.stop();
    m_state = ConnectionState::Disconnected;
    emit stateChanged(m_state);
    emit statusMessage("Disconnected from server");
    scheduleReconnect();
}

void FsdClient::onReadyRead() {
    while (m_socket.canReadLine()) {
        const QString line = QString::fromLatin1(m_socket.readLine()).trimmed();
        if (line.isEmpty()) continue;
        const ParsedPacket packet = FsdParser::parse(line);
        // Handle internally before emitting so callers see correct state
        switch (packet.type) {
            case PacketType::ServerIdent: handleServerIdent(packet); break;
            case PacketType::Ping:        handlePing(packet);        break;
            default: break;
        }
        emit packetReceived(packet);
    }
}

void FsdClient::onErrorOccurred(QAbstractSocket::SocketError) {
    const QString err = m_socket.errorString();
    qDebug() << "[FSD] Socket error:" << err;
    emit statusMessage(QString("Connection error: %1").arg(err));
    m_keepaliveTimer.stop();
    m_state = ConnectionState::Disconnected;
    emit stateChanged(m_state);
    scheduleReconnect();
}

void FsdClient::onKeepaliveTick() {
    if (m_state != ConnectionState::Connected) return;
    sendRaw(m_protocol.buildPing(m_pendingLogin.callsign));
}

void FsdClient::handleServerIdent(const ParsedPacket& packet) {
    Q_UNUSED(packet);
    m_serverIdentReceived = true;
    qDebug() << "[FSD] Server ident received";
    emit statusMessage("Server identified — logging in");
    if (m_loginPending) {
        sendRaw(m_protocol.buildAddPilot(m_pendingLogin));
        m_loginPending = false;
    }
}

void FsdClient::handlePing(const ParsedPacket& packet) {
    // Reply immediately: $POcallsign:SERVER:payload
    const QString payload = packet.fields.size() > 2 ? packet.fields.at(2) : QString();
    sendRaw(m_protocol.buildPong(m_pendingLogin.callsign, payload));
}

void FsdClient::scheduleReconnect() {
    if (m_reconnectAttempts >= MAX_RECONNECT_ATTEMPTS || m_lastHost.isEmpty()) return;
    const int delayMs = RECONNECT_DELAYS_MS[qMin(m_reconnectAttempts, 2)];
    ++m_reconnectAttempts;
    emit statusMessage(QString("Reconnecting in %1 s (attempt %2/%3)…")
        .arg(delayMs / 1000).arg(m_reconnectAttempts).arg(MAX_RECONNECT_ATTEMPTS));
    m_reconnectTimer.start(delayMs);
}

void FsdClient::sendRaw(const QString& line) {
    if (m_socket.state() != QAbstractSocket::ConnectedState) return;
    m_socket.write((line + "\r\n").toLatin1());
}

ConnectionState FsdClient::connectionState() const { return m_state; }

} // namespace SkyHigh::Fsd
