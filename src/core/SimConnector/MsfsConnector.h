#pragma once
#include "ISimConnector.h"
#include <QTimer>
#include <QObject>

// Forward-declare SimConnect handle type so we don't need the SDK header here.
// The SDK is only required on the machine that actually builds with MSFS support.
// Define SKYHIGH_SIMCONNECT=1 in CMake when the SimConnect SDK is available.
typedef void* HANDLE;

namespace SkyHigh {

/// MSFS SimConnect connector.
/// Polls own-aircraft state every 100 ms via the SimConnect SDK.
/// Falls back gracefully (no-op start/stop) when SimConnect is unavailable.
class MsfsConnector : public ISimConnector {
    Q_OBJECT
public:
    explicit MsfsConnector(QObject* parent = nullptr);
    ~MsfsConnector() override;

    void start()  override;
    void stop()   override;
    bool isConnected() const override { return m_connected; }

private slots:
    void onPollTimer();

private:
    void openSimConnect();
    void closeSimConnect();
    void dispatchMessages();

    QTimer m_pollTimer;
    bool   m_connected{false};
    HANDLE m_hSim{nullptr};

    // SimConnect request/definition IDs
    static constexpr int DEF_OWN_AIRCRAFT = 1;
    static constexpr int REQ_OWN_AIRCRAFT = 1;
};

} // namespace SkyHigh
