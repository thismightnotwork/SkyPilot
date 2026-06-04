#pragma once
#include <QObject>
#include <QTcpSocket>
#include <QTimer>
#include "FsdProtocol.h"
#include "FsdPackets.h"

namespace SkyHigh::Fsd {

enum class ConnectionState { Disconnected, Connecting, Connected };

class FsdClient : public QObject {
    Q_OBJECT
public:
    explicit FsdClient(QObject* parent = nullptr);

    void connectToServer(const QString& host, quint16 port);
    void disconnectFromServer();
    void beginLogin(const ConnectRequest& request);
    void sendTextMessage(const QString& to, const QString& message);
    void sendPositionUpdate(const PositionReport& report);
    void sendFlightPlan(const FlightPlanData& fp);
    ConnectionState connectionState() const;

signals:
    void stateChanged(ConnectionState state);
    void statusMessage(const QString& message);
    void packetReceived(const ParsedPacket& packet);

private slots:
    void onConnected();
    void onDisconnected();
    void onReadyRead();
    void onErrorOccurred(QAbstractSocket::SocketError error);
    void onKeepaliveTick();

private:
    void sendRaw(const QString& line);
    void handleServerIdent(const ParsedPacket& packet);
    void handlePing(const ParsedPacket& packet);
    void scheduleReconnect();

    QTcpSocket    m_socket;
    FsdProtocol   m_protocol;
    QTimer        m_keepaliveTimer;   // fires every 30s to send $PI
    QTimer        m_reconnectTimer;   // fires after back-off delay
    ConnectRequest m_pendingLogin;
    bool          m_loginPending{false};
    bool          m_serverIdentReceived{false};
    ConnectionState m_state{ConnectionState::Disconnected};
    int           m_reconnectAttempts{0};
    QString       m_lastHost;
    quint16       m_lastPort{0};
};

} // namespace SkyHigh::Fsd
