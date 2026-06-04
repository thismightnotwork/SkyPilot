#include "FsdProtocol.h"
#include <QDateTime>
#include <QStringList>

namespace SkyHigh::Fsd {

QString FsdProtocol::buildAddPilot(const ConnectRequest& req) {
    // #APcallsign:SERVER:cid:password:pilot_rating:protocol_version:simulator:realname
    return QString("#AP%1:SERVER:%2:%3:1:100:1:%4")
        .arg(req.callsign, req.cid, req.password, req.realName);
}

QString FsdProtocol::buildPilotPosition(const PositionReport& r) {
    // @mode:callsign:squawk:rating:lat:lon:alt:groundspeed:pbh:flags
    return QString("@N:%1:2000:1:%2:%3:%4:%5:0:0")
        .arg(r.callsign)
        .arg(r.latitude,  0, 'f', 6)
        .arg(r.longitude, 0, 'f', 6)
        .arg(r.altitudeFeet)
        .arg(r.groundspeed);
}

QString FsdProtocol::buildTextMessage(const QString& from, const QString& to, const QString& message) {
    return QString("#TM%1:%2:%3").arg(from, to, message);
}

QString FsdProtocol::buildPing(const QString& callsign) {
    return QString("$PI%1:SERVER:%2").arg(callsign).arg(QDateTime::currentMSecsSinceEpoch());
}

QString FsdProtocol::buildPong(const QString& callsign, const QString& payload) {
    return QString("$PO%1:SERVER:%2").arg(callsign, payload);
}

QString FsdProtocol::buildDeletePilot(const QString& callsign) {
    return QString("#DP%1:SERVER").arg(callsign);
}

QString FsdProtocol::buildFlightPlan(const QString& callsign, const FlightPlanData& fp) {
    // $FPcallsign:SERVER:flight_rules:aircraft:TAS:dep:dep_time:act_dep_time:alt:dest:hrs:min:hrs_fuel:min_fuel:alt:remarks:route
    return QString("$FP%1:SERVER:%2:%3:%4:%5:0000:0000:%6:%7:%8:%9:0:0:%10:%11:%12")
        .arg(callsign)
        .arg(fp.flightRules)
        .arg(fp.aircraftIcao)
        .arg(fp.cruiseTas)
        .arg(fp.departure)
        .arg(fp.cruiseAltitude)
        .arg(fp.destination)
        .arg(fp.hoursEnroute).arg(fp.minsEnroute)
        .arg(fp.alternate)
        .arg(fp.remarks)
        .arg(fp.route);
}

} // namespace SkyHigh::Fsd
