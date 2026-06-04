#pragma once
#include "ISimConnector.h"
#include <QUdpSocket>
#include <QTimer>

namespace SkyHigh {

/// X-Plane 11/12 connector via UDP RPOS datagram.
/// X-Plane sends RPOS packets to any external listener; we bind on the
/// standard port 49000 and parse the struct directly.
/// To enable RPOS output in X-Plane: Settings → Data Output → "RPOS" checked,
/// or use the net_out plugin at 49000.
class XPlaneConnector : public ISimConnector {
    Q_OBJECT
public:
    explicit XPlaneConnector(QObject* parent = nullptr);
    ~XPlaneConnector() override;

    void start()  override;
    void stop()   override;
    bool isConnected() const override { return m_connected; }

    /// Port X-Plane sends RPOS datagrams to (default 49000).
    void setListenPort(quint16 port) { m_port = port; }

private slots:
    void onDatagramReady();
    void onStaleTimer();

private:
    void parseRpos(const QByteArray& data);
    void parseDref(const QByteArray& data);

    QUdpSocket m_socket;
    QTimer     m_staleTimer;   // fires if no data for 5 s → simDisconnected
    quint16    m_port{49000};
    bool       m_connected{false};

    // Accumulated state from individual dataref packets
    OwnAircraftData m_ownData;
};

} // namespace SkyHigh
