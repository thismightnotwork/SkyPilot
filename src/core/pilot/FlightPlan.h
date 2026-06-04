#pragma once
#include <QString>
namespace SkyHigh {
struct FlightPlan {
    QString departure; QString destination; QString alternate;
    QString aircraftIcao; QString route; QString remarks;
    int cruiseAltitude{0}; int cruiseTas{0};
    QString flightRules{"I"};
};
}
