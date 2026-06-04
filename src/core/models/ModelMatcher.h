#pragma once
#include <QObject>
#include <QJsonArray>
#include <QHash>

namespace SkyHigh {

/// A lightweight model-matching rule.
struct ModelRule {
    QString callsignPrefix;   // e.g. "BAW"
    QString aircraftIcao;     // e.g. "B738"
    QString airlineIcao;      // e.g. "BAW"
    QString modelPath;        // path to the CSL model package
    int     priority{0};      // higher wins on tie-break
};

/// ModelMatcher resolves an inbound aircraft to the best available
/// CSL / SimObject model path.
///
/// Resolution order (highest priority first):
///   1. Exact callsign prefix + aircraft ICAO + airline ICAO
///   2. Aircraft ICAO + airline ICAO
///   3. Aircraft ICAO only
///   4. Generic fallback ("default")
///
/// Rules are loaded from <appData>/models/rules.json at startup.
/// If no rules file exists a built-in default set is used.
class ModelMatcher : public QObject {
    Q_OBJECT
public:
    explicit ModelMatcher(QObject* parent = nullptr);

    /// Returns the best-matching model path for the given aircraft.
    QString bestMatch(const QString& callsign,
                      const QString& aircraftIcao,
                      const QString& airlineIcao) const;

    /// Load rules from a JSON file.
    bool loadRules(const QString& filePath);

    int ruleCount() const { return m_rules.size(); }

private:
    void loadBuiltinRules();

    QList<ModelRule> m_rules;
    QString          m_fallbackModel{"default"};
};

} // namespace SkyHigh
