#pragma once
#include "AircraftModelSet.h"
namespace SkyHigh {
class ModelMatcher {
public:
    void setModelSet(const AircraftModelSet& set);
    AircraftModel bestMatch(const QString& icaoType, const QString& airline) const;
private:
    AircraftModelSet m_modelSet;
};
}
