#include "PilotSession.h"
namespace SkyHigh {
PilotSession::PilotSession(QObject* parent) : QObject(parent) {}
FlightPlan& PilotSession::flightPlan() { return m_flightPlan; }
}
