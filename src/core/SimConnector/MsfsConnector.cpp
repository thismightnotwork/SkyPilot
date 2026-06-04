#include "MsfsConnector.h"
#include <QDebug>

// ---------------------------------------------------------------------------
// SimConnect SDK integration.
// Set SKYHIGH_SIMCONNECT=1 in CMakeLists.txt when the MSFS SDK is installed.
// Without it the connector compiles and runs but reports "SimConnect SDK not
// available" and never emits positionUpdated.
// ---------------------------------------------------------------------------
#ifdef SKYHIGH_SIMCONNECT
  #include <SimConnect.h>
  #pragma comment(lib, "SimConnect.lib")
#endif

namespace SkyHigh {

#ifdef SKYHIGH_SIMCONNECT
/// SimConnect data definition struct — must match the addToDataDefinition calls exactly.
struct SimOwnAircraft {
    double latitude;          // degrees
    double longitude;         // degrees
    double altitude;          // feet
    double heading;           // degrees magnetic
    double groundspeed;       // knots
    double verticalSpeed;     // feet/min
    double pitch;             // degrees
    double bank;              // degrees
    INT32  onGround;          // bool
    char   atcType[32];       // ICAO type
    char   atcAirline[64];    // airline
};
#endif

MsfsConnector::MsfsConnector(QObject* parent) : ISimConnector(parent) {
    m_pollTimer.setInterval(100);   // 10 Hz
    m_pollTimer.setSingleShot(false);
    connect(&m_pollTimer, &QTimer::timeout, this, &MsfsConnector::onPollTimer);
}

MsfsConnector::~MsfsConnector() {
    stop();
}

void MsfsConnector::start() {
#ifdef SKYHIGH_SIMCONNECT
    emit statusMessage("MSFS: Waiting for SimConnect…");
    openSimConnect();
    m_pollTimer.start();
#else
    emit statusMessage("MSFS: SimConnect SDK not compiled in — build with SKYHIGH_SIMCONNECT=1");
#endif
}

void MsfsConnector::stop() {
    m_pollTimer.stop();
    closeSimConnect();
}

void MsfsConnector::openSimConnect() {
#ifdef SKYHIGH_SIMCONNECT
    HRESULT hr = SimConnect_Open(&m_hSim, "SkyHighPilot", nullptr, 0, nullptr, 0);
    if (SUCCEEDED(hr)) {
        // Register data definition
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "PLANE LATITUDE",         "degrees",      SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "PLANE LONGITUDE",        "degrees",      SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "PLANE ALTITUDE",         "feet",         SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "PLANE HEADING DEGREES MAGNETIC", "degrees", SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "GPS GROUND SPEED",        "knots",        SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "VERTICAL SPEED",          "feet/minute", SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "PLANE PITCH DEGREES",    "degrees",      SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "PLANE BANK DEGREES",     "degrees",      SIMCONNECT_DATATYPE_FLOAT64);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "SIM ON GROUND",          "bool",         SIMCONNECT_DATATYPE_INT32);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "ATC TYPE",               nullptr,        SIMCONNECT_DATATYPE_STRING32);
        SimConnect_AddToDataDefinition(m_hSim, DEF_OWN_AIRCRAFT, "ATC AIRLINE",            nullptr,        SIMCONNECT_DATATYPE_STRING64);
        // Request repeating updates
        SimConnect_RequestDataOnSimObject(m_hSim, REQ_OWN_AIRCRAFT, DEF_OWN_AIRCRAFT,
            SIMCONNECT_OBJECT_ID_USER, SIMCONNECT_PERIOD_SECOND, 0, 0, 0, 0);
        m_connected = true;
        emit simConnected();
        emit statusMessage("MSFS: SimConnect open");
    } else {
        m_hSim = nullptr;
        qDebug() << "[MSFS] SimConnect_Open failed, will retry";
    }
#endif
}

void MsfsConnector::closeSimConnect() {
#ifdef SKYHIGH_SIMCONNECT
    if (m_hSim) {
        SimConnect_Close(m_hSim);
        m_hSim = nullptr;
    }
#endif
    if (m_connected) {
        m_connected = false;
        emit simDisconnected();
    }
}

void MsfsConnector::onPollTimer() {
#ifdef SKYHIGH_SIMCONNECT
    if (!m_hSim) {
        // Retry connection every poll tick until it succeeds
        openSimConnect();
        return;
    }
    dispatchMessages();
#endif
}

void MsfsConnector::dispatchMessages() {
#ifdef SKYHIGH_SIMCONNECT
    SimConnect_CallDispatch(m_hSim, [](SIMCONNECT_RECV* pData, DWORD cbData, void* pContext) {
        auto* self = static_cast<MsfsConnector*>(pContext);
        if (!self) return;
        if (pData->dwID == SIMCONNECT_RECV_ID_SIMOBJECT_DATA) {
            auto* pObjData = static_cast<SIMCONNECT_RECV_SIMOBJECT_DATA*>(pData);
            if (pObjData->dwRequestID == REQ_OWN_AIRCRAFT) {
                auto* d = reinterpret_cast<SimOwnAircraft*>(&pObjData->dwData);
                OwnAircraftData out;
                out.latitude          = d->latitude;
                out.longitude         = d->longitude;
                out.altitudeFeet      = static_cast<int>(d->altitude);
                out.headingDegrees    = static_cast<int>(d->heading);
                out.groundspeedKts    = static_cast<int>(d->groundspeed);
                out.verticalSpeedFpm  = static_cast<int>(d->verticalSpeed);
                out.pitchDegrees      = d->pitch;
                out.bankDegrees       = d->bank;
                out.onGround          = d->onGround != 0;
                out.aircraftIcao      = QString::fromLatin1(d->atcType).trimmed();
                out.airlineIcao       = QString::fromLatin1(d->atcAirline).trimmed();
                emit self->positionUpdated(out);
            }
        } else if (pData->dwID == SIMCONNECT_RECV_ID_QUIT) {
            self->closeSimConnect();
        }
    }, this);
#endif
}

} // namespace SkyHigh
