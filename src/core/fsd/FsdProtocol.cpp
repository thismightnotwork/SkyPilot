#include "FsdProtocol.h"
#include <QStringList>
namespace SkyHigh::Fsd {
QString FsdProtocol::buildAddPilot(const ConnectRequest& req) {
    return QString("#AP%1:SERVER:1234567:%2:1:100:1:%3").arg(req.callsign, req.password, req.realName);
}
QString FsdProtocol::buildPilotPosition(const PositionReport& r) {
    return QString("@N:%1:%2:%3:%4:%5:%6:0").arg(r.callsign).arg(r.latitude,0,'f',6).arg(r.longitude,0,'f',6).arg(r.altitudeFeet).arg(r.groundspeed).arg(r.heading);
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
    return QString("#DP%1").arg(callsign);
}
}
