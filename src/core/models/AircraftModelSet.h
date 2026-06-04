#pragma once
#include <QString>
#include <QList>
namespace SkyHigh {
struct AircraftModel { QString icaoType; QString livery; QString modelPath; };
struct AircraftModelSet { QList<AircraftModel> models; void loadFromDirectory(const QString& path); };
}
