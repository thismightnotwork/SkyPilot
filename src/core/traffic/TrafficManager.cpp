#include "TrafficManager.h"
#include <QDebug>

namespace SkyHigh {

static constexpr int STALE_THRESHOLD_MS   = 60000; // remove after 60 s silence
static constexpr int PRUNE_INTERVAL_MS    = 30000; // check every 30 s
static constexpr int INTERP_INTERVAL_MS   = 100;   // 10 Hz interpolation

TrafficManager::TrafficManager(QObject* parent) : QAbstractListModel(parent) {
    m_pruneTimer.setInterval(PRUNE_INTERVAL_MS);
    m_pruneTimer.setSingleShot(false);
    connect(&m_pruneTimer, &QTimer::timeout, this, &TrafficManager::onPruneTimer);
    m_pruneTimer.start();

    m_interpolateTimer.setInterval(INTERP_INTERVAL_MS);
    m_interpolateTimer.setSingleShot(false);
    connect(&m_interpolateTimer, &QTimer::timeout, this, &TrafficManager::onInterpolateTimer);
    m_interpolateTimer.start();
}

int TrafficManager::rowCount(const QModelIndex& parent) const {
    if (parent.isValid()) return 0;
    return m_aircraft.size();
}

QVariant TrafficManager::data(const QModelIndex& index, int role) const {
    if (!index.isValid() || index.row() >= m_aircraft.size()) return {};
    const TrafficAircraft& a = m_aircraft.at(index.row());
    switch (role) {
        case CallsignRole:       return a.callsign;
        case LatitudeRole:       return a.latitude;
        case LongitudeRole:      return a.longitude;
        case AltitudeFeetRole:   return a.altitudeFeet;
        case HeadingDegreesRole: return a.headingDegrees;
        case GroundspeedRole:    return a.groundspeed;
        case VerticalSpeedRole:  return a.verticalSpeed;
        case OnGroundRole:       return a.onGround;
        case AircraftIcaoRole:   return a.aircraftIcao;
        case AirlineIcaoRole:    return a.airlineIcao;
        case MatchedModelRole:   return a.matchedModelPath;
        case LastSeenRole:       return a.lastSeen.toString(Qt::ISODate);
        default:                 return {};
    }
}

QHash<int, QByteArray> TrafficManager::roleNames() const {
    return {
        {CallsignRole,       "callsign"},
        {LatitudeRole,       "latitude"},
        {LongitudeRole,      "longitude"},
        {AltitudeFeetRole,   "altitudeFeet"},
        {HeadingDegreesRole, "headingDegrees"},
        {GroundspeedRole,    "groundspeed"},
        {VerticalSpeedRole,  "verticalSpeed"},
        {OnGroundRole,       "onGround"},
        {AircraftIcaoRole,   "aircraftIcao"},
        {AirlineIcaoRole,    "airlineIcao"},
        {MatchedModelRole,   "matchedModel"},
        {LastSeenRole,       "lastSeen"},
    };
}

void TrafficManager::upsertFromPositionPacket(const Fsd::PositionPacket& pkt) {
    const qint64 nowMs = QDateTime::currentMSecsSinceEpoch();
    int row = indexOfCallsign(pkt.callsign);

    if (row < 0) {
        // New aircraft
        TrafficAircraft a;
        a.callsign         = pkt.callsign;
        a.latitude         = pkt.latitude;
        a.longitude        = pkt.longitude;
        a.altitudeFeet     = pkt.altitudeFeet;
        a.headingDegrees   = pkt.headingDegrees;
        a.groundspeed      = pkt.groundspeed;
        a.verticalSpeed    = pkt.verticalSpeed;
        a.onGround         = pkt.onGround;
        a.isFastUpdate     = pkt.isFastUpdate;
        a.lastUpdateMs     = nowMs;
        a.firstSeen        = QDateTime::currentDateTimeUtc();
        a.lastSeen         = QDateTime::currentDateTimeUtc();
        // Model match
        a.matchedModelPath = m_modelMatcher.bestMatch(pkt.callsign, pkt.aircraftIcao, pkt.airlineIcao);
        row = m_aircraft.size();
        beginInsertRows({}, row, row);
        m_aircraft.append(a);
        m_callsignIndex[pkt.callsign] = row;
        endInsertRows();
        qDebug() << "[Traffic] New:" << pkt.callsign << "model:" << a.matchedModelPath;
    } else {
        TrafficAircraft& a = m_aircraft[row];

        if (pkt.isFastUpdate) {
            // Fast-update (^): skip interpolation reset, just nudge target
            a.latitude       = pkt.latitude;
            a.longitude      = pkt.longitude;
            a.altitudeFeet   = pkt.altitudeFeet;
            a.headingDegrees = pkt.headingDegrees;
            a.groundspeed    = pkt.groundspeed;
            a.verticalSpeed  = pkt.verticalSpeed;
        } else {
            // Full update (@): set new interpolation target
            a.prevLatitude        = a.latitude;
            a.prevLongitude       = a.longitude;
            a.prevAltitudeFeet    = a.altitudeFeet;
            a.prevHeadingDegrees  = a.headingDegrees;
            a.updateIntervalMs    = nowMs - a.lastUpdateMs;
            a.interpolating       = true;

            a.latitude       = pkt.latitude;
            a.longitude      = pkt.longitude;
            a.altitudeFeet   = pkt.altitudeFeet;
            a.headingDegrees = pkt.headingDegrees;
            a.groundspeed    = pkt.groundspeed;
            a.verticalSpeed  = pkt.verticalSpeed;
            a.onGround       = pkt.onGround;
        }
        a.lastUpdateMs = nowMs;
        a.lastSeen     = QDateTime::currentDateTimeUtc();
        emit dataChanged(index(row), index(row));
    }
}

void TrafficManager::removeByCallsign(const QString& callsign) {
    const int row = indexOfCallsign(callsign);
    if (row < 0) return;
    beginRemoveRows({}, row, row);
    m_aircraft.removeAt(row);
    // Rebuild index
    m_callsignIndex.clear();
    for (int i = 0; i < m_aircraft.size(); ++i)
        m_callsignIndex[m_aircraft[i].callsign] = i;
    endRemoveRows();
}

void TrafficManager::onPruneTimer() {
    const qint64 nowMs  = QDateTime::currentMSecsSinceEpoch();
    QStringList toRemove;
    for (const TrafficAircraft& a : m_aircraft) {
        if ((nowMs - a.lastUpdateMs) > STALE_THRESHOLD_MS)
            toRemove << a.callsign;
    }
    for (const QString& cs : toRemove) {
        qDebug() << "[Traffic] Pruning stale:" << cs;
        removeByCallsign(cs);
    }
}

void TrafficManager::onInterpolateTimer() {
    // Simple linear interpolation toward the target position.
    // This gives smooth movement between 5-second FSD updates.
    // Not emitting dataChanged here for every aircraft every 100ms would be
    // too expensive — we batch them and only update rows that are interpolating.
    const qint64 nowMs = QDateTime::currentMSecsSinceEpoch();
    for (int i = 0; i < m_aircraft.size(); ++i) {
        TrafficAircraft& a = m_aircraft[i];
        if (!a.interpolating || a.updateIntervalMs <= 0) continue;

        const double elapsed = static_cast<double>(nowMs - a.lastUpdateMs);
        // Alpha: how far through this update interval are we?
        // Clamp to [0,1] — don't extrapolate beyond the target.
        const double alpha = qBound(0.0, elapsed / static_cast<double>(a.updateIntervalMs), 1.0);

        // Interpolate from previous to current target
        // (current values stored in a.latitude etc ARE the target already;
        //  we store the previous snapshot)
        const double interLat = a.prevLatitude   + (a.latitude    - a.prevLatitude)   * alpha;
        const double interLon = a.prevLongitude  + (a.longitude   - a.prevLongitude)  * alpha;
        const int    interAlt = a.prevAltitudeFeet + static_cast<int>((a.altitudeFeet - a.prevAltitudeFeet) * alpha);

        // Only update the model if values actually changed meaningfully
        if (qAbs(interLat - a.prevLatitude) > 1e-7 || qAbs(interLon - a.prevLongitude) > 1e-7) {
            // Temporarily overwrite prev fields with interpolated values for rendering
            // (the true target remains untouched)
            // We write directly into the list since this is a private timer slot
            a.prevLatitude      = interLat;
            a.prevLongitude     = interLon;
            a.prevAltitudeFeet  = interAlt;
            emit dataChanged(index(i), index(i), {LatitudeRole, LongitudeRole, AltitudeFeetRole});
        }

        if (alpha >= 1.0) a.interpolating = false;
    }
}

int TrafficManager::indexOfCallsign(const QString& callsign) const {
    return m_callsignIndex.value(callsign, -1);
}

} // namespace SkyHigh
