#pragma once
#include <QObject>
#include "core/fsd/FsdClient.h"
#include "core/messages/MessageManager.h"
#include "core/traffic/TrafficManager.h"

namespace SkyHigh {
class ConnectionManager : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString status READ status NOTIFY statusChanged)
    Q_PROPERTY(bool connected READ connected NOTIFY connectedChanged)
    Q_PROPERTY(QObject* messagesModel READ messagesModel CONSTANT)
    Q_PROPERTY(QObject* trafficModel READ trafficModel CONSTANT)
    Q_PROPERTY(int unreadMessages READ unreadMessages NOTIFY unreadMessagesChanged)
    Q_PROPERTY(int trafficCount READ trafficCount NOTIFY trafficCountChanged)
public:
    explicit ConnectionManager(QObject* parent = nullptr);
    QString status() const;
    bool connected() const;
    QObject* messagesModel();
    QObject* trafficModel();
    int unreadMessages() const;
    int trafficCount() const;
    Q_INVOKABLE void connectPilot(const QString& callsign, const QString& cid, const QString& password);
    Q_INVOKABLE void disconnectPilot();
signals:
    void statusChanged();
    void connectedChanged();
    void unreadMessagesChanged();
    void trafficCountChanged();
private:
    QString m_status;
    bool m_connected{false};
    Fsd::FsdClient m_fsdClient;
    MessageManager m_messages;
    TrafficManager m_traffic;
};
}
