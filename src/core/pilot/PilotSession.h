#pragma once
#include <QObject>
#include <QString>
#include "FlightPlan.h"
namespace SkyHigh {
class PilotSession : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString callsign MEMBER m_callsign NOTIFY sessionChanged)
    Q_PROPERTY(QString aircraftType MEMBER m_aircraftType NOTIFY sessionChanged)
public:
    explicit PilotSession(QObject* parent = nullptr);
    FlightPlan& flightPlan();
signals:
    void sessionChanged();
private:
    QString m_callsign;
    QString m_aircraftType{"A20N"};
    FlightPlan m_flightPlan;
};
}
