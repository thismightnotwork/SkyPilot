#pragma once
#include <QObject>
#include <QTcpSocket>
namespace SkyHigh {
class MumbleClient : public QObject {
    Q_OBJECT
    Q_PROPERTY(bool connected READ isConnected NOTIFY connectedChanged)
    Q_PROPERTY(bool transmitting READ isTransmitting NOTIFY transmittingChanged)
public:
    explicit MumbleClient(QObject* parent = nullptr);
    bool isConnected() const;
    bool isTransmitting() const;
    Q_INVOKABLE void connectToServer(const QString& host, quint16 port, const QString& username);
    Q_INVOKABLE void disconnect();
    Q_INVOKABLE void setPtt(bool active);
signals:
    void connectedChanged();
    void transmittingChanged();
private:
    QTcpSocket m_socket;
    bool m_connected{false};
    bool m_transmitting{false};
};
}
