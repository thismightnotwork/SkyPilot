#include "XPlaneConnector.h"
#include <QNetworkDatagram>
#include <QDebug>
#include <cstring>
#include <cmath>

namespace SkyHigh {

// ---------------------------------------------------------------------------
// X-Plane RPOS packet layout (44 bytes of doubles/floats after the 5-byte header)
// Header: "RPOS\0" (5 bytes)
// Body:   lon(d) lat(d) ele_msl(d) ele_agl(f) pitch(f) roll(f) hdgt(f)
//         vx(f) vy(f) vz(f) P(f) Q(f) R(f)
// ---------------------------------------------------------------------------
#pragma pack(push,1)
struct XpRposBody {
    double lon_deg;
    double lat_deg;
    double ele_msl_m;     // elevation MSL in metres
    float  ele_agl_m;
    float  pitch_deg;     // nose-up positive
    float  roll_deg;      // right-wing-down positive
    float  hdg_true_deg;
    float  vx_mps;        // east velocity m/s
    float  vy_mps;        // up velocity m/s
    float  vz_mps;        // south velocity m/s
    float  P_rads;        // roll rate
    float  Q_rads;        // pitch rate
    float  R_rads;        // yaw rate
};
#pragma pack(pop)

static constexpr double MPS_TO_KNOTS = 1.94384;
static constexpr double M_TO_FEET    = 3.28084;

XPlaneConnector::XPlaneConnector(QObject* parent) : ISimConnector(parent) {
    // Stale-data watchdog — if X-Plane stops sending for 5 s we report disconnected
    m_staleTimer.setInterval(5000);
    m_staleTimer.setSingleShot(true);
    connect(&m_staleTimer, &QTimer::timeout, this, &XPlaneConnector::onStaleTimer);
    connect(&m_socket, &QUdpSocket::readyRead, this, &XPlaneConnector::onDatagramReady);
}

XPlaneConnector::~XPlaneConnector() {
    stop();
}

void XPlaneConnector::start() {
    if (!m_socket.bind(QHostAddress::LocalHost, m_port,
                       QAbstractSocket::ShareAddress | QAbstractSocket::ReuseAddressHint)) {
        emit statusMessage(QString("X-Plane: cannot bind UDP port %1 — %2")
                           .arg(m_port).arg(m_socket.errorString()));
        return;
    }
    emit statusMessage(QString("X-Plane: listening on UDP %1").arg(m_port));
}

void XPlaneConnector::stop() {
    m_staleTimer.stop();
    m_socket.close();
    if (m_connected) {
        m_connected = false;
        emit simDisconnected();
    }
}

void XPlaneConnector::onDatagramReady() {
    while (m_socket.hasPendingDatagrams()) {
        const QNetworkDatagram dg = m_socket.receiveDatagram();
        const QByteArray data = dg.data();
        if (data.size() < 5) continue;

        // Reset the stale watchdog every time we receive valid data
        m_staleTimer.start();

        if (!m_connected) {
            m_connected = true;
            emit simConnected();
            emit statusMessage("X-Plane: data received — connected");
        }

        const QByteArray tag = data.left(4);
        if (tag == "RPOS") {
            parseRpos(data);
        }
        // Future: DREF packets for individual dataref subscription
    }
}

void XPlaneConnector::parseRpos(const QByteArray& data) {
    // RPOS\0 header is 5 bytes; body starts at offset 5
    if (data.size() < 5 + static_cast<int>(sizeof(XpRposBody))) return;

    XpRposBody body;
    std::memcpy(&body, data.constData() + 5, sizeof(body));

    // Ground speed from velocity vector (XY plane)
    const double gs_mps = std::sqrt(body.vx_mps * body.vx_mps +
                                     body.vz_mps * body.vz_mps);

    m_ownData.latitude         = body.lat_deg;
    m_ownData.longitude        = body.lon_deg;
    m_ownData.altitudeFeet     = static_cast<int>(body.ele_msl_m * M_TO_FEET);
    m_ownData.headingDegrees   = static_cast<int>(body.hdg_true_deg);
    m_ownData.groundspeedKts   = static_cast<int>(gs_mps * MPS_TO_KNOTS);
    m_ownData.verticalSpeedFpm = static_cast<int>(body.vy_mps * M_TO_FEET * 60.0);
    m_ownData.pitchDegrees     = body.pitch_deg;
    m_ownData.bankDegrees      = body.roll_deg;
    // X-Plane doesn't give on-ground via RPOS; infer from AGL altitude
    m_ownData.onGround         = (body.ele_agl_m < 0.5f);

    emit positionUpdated(m_ownData);
}

void XPlaneConnector::onStaleTimer() {
    qDebug() << "[XPlane] No data for 5 s — marking disconnected";
    emit statusMessage("X-Plane: no data — sim may have stopped");
    m_connected = false;
    emit simDisconnected();
}

} // namespace SkyHigh
