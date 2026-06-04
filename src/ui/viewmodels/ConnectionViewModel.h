#pragma once
#include <QObject>
#include "core/network/ConnectionManager.h"

namespace SkyHigh {

class ConnectionViewModel : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString  callsign       MEMBER m_callsign  NOTIFY formChanged)
    Q_PROPERTY(QString  cid            MEMBER m_cid       NOTIFY formChanged)
    Q_PROPERTY(QString  password       MEMBER m_password  NOTIFY formChanged)
    Q_PROPERTY(QString  status         READ status         NOTIFY statusChanged)
    Q_PROPERTY(bool     connected      READ connected      NOTIFY connectedChanged)
    Q_PROPERTY(QObject* messagesModel  READ messagesModel  CONSTANT)
    Q_PROPERTY(QObject* trafficModel   READ trafficModel   CONSTANT)
    Q_PROPERTY(int      unreadMessages READ unreadMessages NOTIFY unreadMessagesChanged)
    Q_PROPERTY(int      trafficCount   READ trafficCount   NOTIFY trafficCountChanged)
public:
    explicit ConnectionViewModel(QObject* parent = nullptr);

    QString  status()         const;
    bool     connected()      const;
    QObject* messagesModel()  const;
    QObject* trafficModel()   const;
    int      unreadMessages() const;
    int      trafficCount()   const;

    Q_INVOKABLE void connectOrDisconnect();
    Q_INVOKABLE void sendMessage(const QString& channel, const QString& text);

signals:
    void formChanged();
    void statusChanged();
    void connectedChanged();
    void unreadMessagesChanged();
    void trafficCountChanged();

private:
    QString           m_callsign{"SKY123"};
    QString           m_cid;
    QString           m_password;
    ConnectionManager m_manager;
};

} // namespace SkyHigh
