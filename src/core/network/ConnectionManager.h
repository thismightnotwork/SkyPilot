#pragma once
#include <QObject>
#include <QTimer>
#include "core/fsd/FsdClient.h"
#include "core/messages/MessageManager.h"
#include "core/traffic/TrafficManager.h"

namespace SkyHigh {

class ConnectionManager : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString  status         READ status         NOTIFY statusChanged)
    Q_PROPERTY(bool     connected      READ connected      NOTIFY connectedChanged)
    Q_PROPERTY(QObject* messagesModel  READ messagesModel  CONSTANT)
    Q_PROPERTY(QObject* trafficModel   READ trafficModel   CONSTANT)
    Q_PROPERTY(int      unreadMessages READ unreadMessages NOTIFY unreadMessagesChanged)
    Q_PROPERTY(int      trafficCount   READ trafficCount   NOTIFY trafficCountChanged)
public:
    explicit ConnectionManager(QObject* parent = nullptr);

    QString  status()         const;
    bool     connected()      const;
    QObject* messagesModel();
    QObject* trafficModel();
    int      unreadMessages() const;
    int      trafficCount()   const;

    Q_INVOKABLE void connectPilot(const QString& callsign, const QString& cid, const QString& password);
    Q_INVOKABLE void disconnectPilot();
    void sendTextMessage(const QString& to, const QString& text);
    void updateOwnPosition(double lat, double lon, int altFt, int hdg, int gs);

signals:
    void statusChanged();
    void connectedChanged();
    void unreadMessagesChanged();
    void trafficCountChanged();

private slots:
    void onPositionTimerTick();

private:
    QString  m_status;
    QString  m_callsign;
    bool     m_connected{false};
    double   m_ownLat{51.148};
    double   m_ownLon{-0.190};
    int      m_ownAlt{0};
    int      m_ownHdg{0};

    Fsd::FsdClient  m_fsdClient;
    MessageManager  m_messages;
    TrafficManager  m_traffic;
    QTimer          m_positionTimer;
};

} // namespace SkyHigh
