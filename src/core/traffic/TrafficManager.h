#pragma once
#include <QAbstractListModel>
#include <QDateTime>
#include <QTimer>
#include "core/fsd/FsdPackets.h"
namespace SkyHigh {
struct RemoteAircraftState {
    QString callsign; double lastLatitude{0.0}; double lastLongitude{0.0};
    double displayLatitude{0.0}; double displayLongitude{0.0};
    int altitudeFeet{0}; int groundspeed{0}; int headingDegrees{0};
    QDateTime lastUpdateUtc; bool fastUpdate{false};
};
class TrafficManager : public QAbstractListModel {
    Q_OBJECT
public:
    enum Roles { CallsignRole = Qt::UserRole + 1, LatitudeRole, LongitudeRole, AltitudeRole, GroundspeedRole, HeadingRole, AgeSecondsRole };
    explicit TrafficManager(QObject* parent = nullptr);
    int rowCount(const QModelIndex& parent = QModelIndex()) const override;
    QVariant data(const QModelIndex& index, int role = Qt::DisplayRole) const override;
    QHash<int, QByteArray> roleNames() const override;
    void upsertFromPositionPacket(const SkyHigh::Fsd::PositionPacket& packet);
    void removeByCallsign(const QString& callsign);
    int aircraftCount() const;
private slots:
    void onInterpolationTick();
private:
    QList<RemoteAircraftState> m_aircraft;
    QTimer m_interpolationTimer;
};
}
