#include "ModelMatcher.h"
namespace SkyHigh {
void ModelMatcher::setModelSet(const AircraftModelSet& set) { m_modelSet = set; }
AircraftModel ModelMatcher::bestMatch(const QString& icaoType, const QString& airline) const {
    Q_UNUSED(airline);
    for (const auto& model : m_modelSet.models) if (model.icaoType == icaoType) return model;
    return m_modelSet.models.isEmpty() ? AircraftModel{} : m_modelSet.models.first();
}
}
