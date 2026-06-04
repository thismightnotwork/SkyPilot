#pragma once
#include <QObject>
#include "core/fsd/FsdProtocol.h"

namespace SkyHigh {

/// Sim-agnostic position data emitted by every connector.
struct OwnAircraftData {
    double  latitude{0.0};
    double  longitude{0.0};
    int     altitudeFeet{0};
    int     headingDegrees{0};
    int     groundspeedKts{0};
    int     verticalSpeedFpm{0};
    double  pitchDegrees{0.0};
    double  bankDegrees{0.0};
    bool    onGround{true};
    QString aircraftIcao{"A20N"};
    QString airlineIcao{"SKY"};
};

class ISimConnector : public QObject {
    Q_OBJECT
public:
    explicit ISimConnector(QObject* parent = nullptr) : QObject(parent) {}
    virtual ~ISimConnector() = default;

    virtual void start()  = 0;
    virtual void stop()   = 0;
    virtual bool isConnected() const = 0;

signals:
    void positionUpdated(const OwnAircraftData& data);
    void simConnected();
    void simDisconnected();
    void statusMessage(const QString& msg);
};

} // namespace SkyHigh
