#pragma once
#include <QObject>
#include <QTcpSocket>
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
private:
    void sendRaw(const QString& line);
    QTcpSocket m_socket;
    FsdProtocol m_protocol;
    ConnectRequest m_pendingLogin;
    bool m_loginPending{false};
    ConnectionState m_state{ConnectionState::Disconnected};
};
}
