#pragma once
#include <QObject>
#include "core/network/ConnectionManager.h"
#include "core/SimConnector/ISimConnector.h"
#include "core/SimConnector/MsfsConnector.h"
#include "core/SimConnector/XPlaneConnector.h"

namespace SkyHigh {

enum class SimType { None = 0, MSFS = 1, XPlane = 2 };

class ConnectionViewModel : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString  callsign        MEMBER m_callsign  NOTIFY formChanged)
    Q_PROPERTY(QString  cid             MEMBER m_cid       NOTIFY formChanged)
    Q_PROPERTY(QString  password        MEMBER m_password  NOTIFY formChanged)
    Q_PROPERTY(QString  status          READ status          NOTIFY statusChanged)
    Q_PROPERTY(bool     connected       READ connected       NOTIFY connectedChanged)
    Q_PROPERTY(bool     simConnected    READ simConnected    NOTIFY simConnectedChanged)
    Q_PROPERTY(QString  simStatus       READ simStatus       NOTIFY simStatusChanged)
    Q_PROPERTY(QString  ownPositionText READ ownPositionText NOTIFY ownPositionChanged)
    Q_PROPERTY(double   ownLat          READ ownLat          NOTIFY ownPositionChanged)
    Q_PROPERTY(double   ownLon          READ ownLon          NOTIFY ownPositionChanged)
    Q_PROPERTY(QObject* messagesModel   READ messagesModel   CONSTANT)
    Q_PROPERTY(QObject* trafficModel    READ trafficModel    CONSTANT)
    Q_PROPERTY(int      unreadMessages  READ unreadMessages  NOTIFY unreadMessagesChanged)
    Q_PROPERTY(int      trafficCount    READ trafficCount    NOTIFY trafficCountChanged)
public:
    explicit ConnectionViewModel(QObject* parent = nullptr);

    QString  status()          const;
    bool     connected()       const;
    bool     simConnected()    const { return m_simConnected; }
    QString  simStatus()       const { return m_simStatus; }
    QString  ownPositionText() const;
    double   ownLat()          const { return m_ownData.latitude; }
    double   ownLon()          const { return m_ownData.longitude; }
    QObject* messagesModel()   const;
    QObject* trafficModel()    const;
    int      unreadMessages()  const;
    int      trafficCount()    const;

    Q_INVOKABLE void connectOrDisconnect();
    Q_INVOKABLE void sendMessage(const QString& channel, const QString& text);
    Q_INVOKABLE void setSimType(int index);   // 0=MSFS, 1=XPlane, 2=None

signals:
    void formChanged();
    void statusChanged();
    void connectedChanged();
    void simConnectedChanged();
    void simStatusChanged();
    void ownPositionChanged();
    void unreadMessagesChanged();
    void trafficCountChanged();

private:
    void attachSimConnector(ISimConnector* connector);
    void detachSimConnector();

    QString  m_callsign{"SKY123"};
    QString  m_cid;
    QString  m_password;
    bool     m_simConnected{false};
    QString  m_simStatus{"No simulator selected"};
    OwnAircraftData m_ownData;

    ConnectionManager  m_manager;
    MsfsConnector      m_msfsConnector;
    XPlaneConnector    m_xplaneConnector;
    ISimConnector*     m_activeConnector{nullptr};
};

} // namespace SkyHigh
