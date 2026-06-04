#pragma once
#include <QAbstractListModel>
#include <QHash>
#include <QTimer>
#include <QDateTime>
#include "core/fsd/FsdPackets.h"
#include "core/models/ModelMatcher.h"

namespace SkyHigh {

/// One aircraft on the network.
struct TrafficAircraft {
    // Identity
    QString callsign;
    QString squawk{"2000"};
    QString flightPlanOrigin;
    QString flightPlanDest;
    QString aircraftIcao{"A20N"};
    QString airlineIcao;
    QString matchedModelPath;  // resolved CSL model path from ModelMatcher

    // Current position (target state for interpolation)
    double  latitude{0.0};
    double  longitude{0.0};
    int     altitudeFeet{0};
    int     headingDegrees{0};
    int     groundspeed{0};
    int     verticalSpeed{0};
    bool    onGround{false};

    // Interpolation state
    double  prevLatitude{0.0};
    double  prevLongitude{0.0};
    int     prevAltitudeFeet{0};
    int     prevHeadingDegrees{0};
    bool    interpolating{false};
    qint64  lastUpdateMs{0};
    qint64  updateIntervalMs{5000};  // typical FSD rate

    // Metadata
    QDateTime firstSeen;
    QDateTime lastSeen;
    bool    isFastUpdate{false};
};

class TrafficManager : public QAbstractListModel {
    Q_OBJECT
public:
    enum TrafficRoles {
        CallsignRole = Qt::UserRole + 1,
        LatitudeRole,
        LongitudeRole,
        AltitudeFeetRole,
        HeadingDegreesRole,
        GroundspeedRole,
        VerticalSpeedRole,
        OnGroundRole,
        AircraftIcaoRole,
        AirlineIcaoRole,
        MatchedModelRole,
        LastSeenRole
    };

    explicit TrafficManager(QObject* parent = nullptr);

    // QAbstractListModel interface
    int rowCount(const QModelIndex& parent = {}) const override;
    QVariant data(const QModelIndex& index, int role) const override;
    QHash<int, QByteArray> roleNames() const override;

    void upsertFromPositionPacket(const Fsd::PositionPacket& packet);
    void removeByCallsign(const QString& callsign);
    int  aircraftCount() const { return m_aircraft.size(); }

private slots:
    void onPruneTimer();
    void onInterpolateTimer();

private:
    int  indexOfCallsign(const QString& callsign) const;

    QList<TrafficAircraft>  m_aircraft;
    QHash<QString, int>     m_callsignIndex;  // callsign → row
    ModelMatcher            m_modelMatcher;
    QTimer                  m_pruneTimer;         // removes stale aircraft every 30 s
    QTimer                  m_interpolateTimer;   // smooth position updates at 10 Hz
};

} // namespace SkyHigh
