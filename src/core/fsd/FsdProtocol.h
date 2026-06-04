#pragma once
#include <QString>

namespace SkyHigh::Fsd {

struct ConnectRequest {
    QString callsign;
    QString cid;
    QString password;
    QString realName;
    QString simulatorType{"MSFS2024"};
};

struct PositionReport {
    QString callsign;
    double  latitude{0.0};
    double  longitude{0.0};
    int     altitudeFeet{0};
    int     groundspeed{0};
    int     heading{0};
    int     verticalSpeed{0};
};

struct FlightPlanData {
    QString departure;
    QString destination;
    QString alternate;
    QString aircraftIcao{"A20N"};
    QString route;
    QString remarks;
    QString flightRules{"I"};
    int     cruiseAltitude{0};
    int     cruiseTas{0};
    int     hoursEnroute{0};
    int     minsEnroute{0};
};

class FsdProtocol {
public:
    QString buildAddPilot(const ConnectRequest& request);
    QString buildPilotPosition(const PositionReport& report);
    QString buildTextMessage(const QString& from, const QString& to, const QString& message);
    QString buildPing(const QString& callsign);
    QString buildPong(const QString& callsign, const QString& payload);
    QString buildDeletePilot(const QString& callsign);
    QString buildFlightPlan(const QString& callsign, const FlightPlanData& fp);
};

} // namespace SkyHigh::Fsd
