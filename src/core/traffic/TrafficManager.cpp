#include "TrafficManager.h"
#include <cmath>
namespace SkyHigh {
TrafficManager::TrafficManager(QObject* parent) : QAbstractListModel(parent) {
    connect(&m_interpolationTimer, &QTimer::timeout, this, &TrafficManager::onInterpolationTick);
    m_interpolationTimer.start(1000);
}
int TrafficManager::rowCount(const QModelIndex& parent) const { return parent.isValid() ? 0 : m_aircraft.size(); }
QVariant TrafficManager::data(const QModelIndex& index, int role) const {
    if (!index.isValid() || index.row() < 0 || index.row() >= m_aircraft.size()) return {};
    const auto& ac = m_aircraft.at(index.row());
    switch (role) {
        case CallsignRole: return ac.callsign;
        case LatitudeRole: return ac.displayLatitude;
        case LongitudeRole: return ac.displayLongitude;
        case AltitudeRole: return ac.altitudeFeet;
        case GroundspeedRole: return ac.groundspeed;
        case HeadingRole: return ac.headingDegrees;
        case AgeSecondsRole: return ac.lastUpdateUtc.secsTo(QDateTime::currentDateTimeUtc()) * -1;
        default: return {};
    }
}
QHash<int, QByteArray> TrafficManager::roleNames() const {
    return {{CallsignRole,"callsign"},{LatitudeRole,"latitude"},{LongitudeRole,"longitude"},{AltitudeRole,"altitudeFeet"},{GroundspeedRole,"groundspeed"},{HeadingRole,"headingDegrees"},{AgeSecondsRole,"ageSeconds"}};
}
void TrafficManager::upsertFromPositionPacket(const SkyHigh::Fsd::PositionPacket& packet) {
    for (int i = 0; i < m_aircraft.size(); ++i) {
        auto& ac = m_aircraft[i];
        if (ac.callsign == packet.callsign) {
            ac.lastLatitude = packet.latitude; ac.lastLongitude = packet.longitude;
            ac.displayLatitude = packet.latitude; ac.displayLongitude = packet.longitude;
            ac.altitudeFeet = packet.altitudeFeet; ac.groundspeed = packet.groundspeed; ac.headingDegrees = packet.headingDegrees;
            ac.lastUpdateUtc = QDateTime::currentDateTimeUtc(); ac.fastUpdate = packet.fastUpdate; emit dataChanged(index(i), index(i)); return;
        }
    }
    beginInsertRows(QModelIndex(), m_aircraft.size(), m_aircraft.size());
    RemoteAircraftState ac; ac.callsign = packet.callsign; ac.lastLatitude = packet.latitude; ac.lastLongitude = packet.longitude;
    ac.displayLatitude = packet.latitude; ac.displayLongitude = packet.longitude; ac.altitudeFeet = packet.altitudeFeet; ac.groundspeed = packet.groundspeed;
    ac.headingDegrees = packet.headingDegrees; ac.fastUpdate = packet.fastUpdate; ac.lastUpdateUtc = QDateTime::currentDateTimeUtc(); m_aircraft.push_back(ac);
    endInsertRows();
}
void TrafficManager::removeByCallsign(const QString& callsign) {
    for (int i = 0; i < m_aircraft.size(); ++i) if (m_aircraft.at(i).callsign == callsign) { beginRemoveRows(QModelIndex(), i, i); m_aircraft.removeAt(i); endRemoveRows(); return; }
}
int TrafficManager::aircraftCount() const { return m_aircraft.size(); }
void TrafficManager::onInterpolationTick() {
    const auto now = QDateTime::currentDateTimeUtc();
    for (int i = 0; i < m_aircraft.size(); ++i) {
        auto& ac = m_aircraft[i];
        const qint64 age = ac.lastUpdateUtc.msecsTo(now);
        const double seconds = static_cast<double>(age) / 1000.0;
        const double nmPerSec = static_cast<double>(ac.groundspeed) / 3600.0;
        const double deltaDegrees = (nmPerSec * seconds) / 60.0;
        const double radians = ac.headingDegrees * 3.14159265358979323846 / 180.0;
        ac.displayLatitude = ac.lastLatitude + deltaDegrees * std::cos(radians);
        ac.displayLongitude = ac.lastLongitude + deltaDegrees * std::sin(radians);
        emit dataChanged(index(i), index(i));
    }
}
}
