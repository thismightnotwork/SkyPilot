#include "ModelMatcher.h"
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QDebug>
#include <QStandardPaths>

namespace SkyHigh {

ModelMatcher::ModelMatcher(QObject* parent) : QObject(parent) {
    // Try to load rules from the app data directory first.
    const QString rulesPath = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation)
                              + "/models/rules.json";
    if (!loadRules(rulesPath)) {
        qDebug() << "[ModelMatcher] No rules file at" << rulesPath << "— using built-ins";
        loadBuiltinRules();
    }
    qDebug() << "[ModelMatcher] Loaded" << m_rules.size() << "rules";
}

QString ModelMatcher::bestMatch(const QString& callsign,
                                 const QString& aircraftIcao,
                                 const QString& airlineIcao) const {
    const QString csPrefix3 = callsign.left(3).toUpper();
    const QString icao      = aircraftIcao.toUpper();
    const QString airline   = airlineIcao.toUpper();

    const ModelRule* best = nullptr;
    int              bestScore = -1;

    for (const ModelRule& rule : m_rules) {
        int score = 0;

        // Aircraft ICAO must match if rule specifies one
        if (!rule.aircraftIcao.isEmpty() && rule.aircraftIcao.toUpper() != icao)
            continue;

        if (!rule.aircraftIcao.isEmpty())   score += 100;
        if (!rule.airlineIcao.isEmpty()  && rule.airlineIcao.toUpper()  == airline) score += 50;
        if (!rule.callsignPrefix.isEmpty()&& rule.callsignPrefix.toUpper() == csPrefix3) score += 25;
        score += rule.priority;

        if (score > bestScore) {
            bestScore = score;
            best = &rule;
        }
    }

    if (best) return best->modelPath;
    return m_fallbackModel;
}

bool ModelMatcher::loadRules(const QString& filePath) {
    QFile f(filePath);
    if (!f.open(QIODevice::ReadOnly)) return false;
    const QJsonDocument doc = QJsonDocument::fromJson(f.readAll());
    if (!doc.isObject()) return false;

    const QJsonObject root = doc.object();
    if (root.contains("fallback"))
        m_fallbackModel = root.value("fallback").toString(m_fallbackModel);

    const QJsonArray rules = root.value("rules").toArray();
    for (const auto& v : rules) {
        const QJsonObject o = v.toObject();
        ModelRule r;
        r.callsignPrefix = o.value("callsign_prefix").toString();
        r.aircraftIcao   = o.value("aircraft_icao").toString();
        r.airlineIcao    = o.value("airline_icao").toString();
        r.modelPath      = o.value("model_path").toString();
        r.priority       = o.value("priority").toInt(0);
        if (!r.modelPath.isEmpty())
            m_rules.append(r);
    }
    return !m_rules.isEmpty();
}

void ModelMatcher::loadBuiltinRules() {
    // A minimal set of common aircraft so traffic shows something sensible
    // without requiring an external rules file.
    // Extend this list or replace with rules.json for production use.
    const struct { const char* icao; const char* path; } defaults[] = {
        {"A20N", "CSL/Airbus/A320neo/A320neo"},
        {"A321", "CSL/Airbus/A321/A321"},
        {"A332", "CSL/Airbus/A330/A330-200"},
        {"A333", "CSL/Airbus/A330/A330-300"},
        {"A359", "CSL/Airbus/A350/A350-900"},
        {"B737", "CSL/Boeing/B737/B737-700"},
        {"B738", "CSL/Boeing/B737/B737-800"},
        {"B739", "CSL/Boeing/B737/B737-900"},
        {"B77W", "CSL/Boeing/B777/B777-300ER"},
        {"B788", "CSL/Boeing/B787/B787-8"},
        {"B789", "CSL/Boeing/B787/B787-9"},
        {"C172", "CSL/Cessna/C172/C172"},
        {"C208", "CSL/Cessna/C208/C208"},
        {"DH8D", "CSL/Bombardier/DHC8/DHC8-400"},
        {"E190", "CSL/Embraer/E190/E190"},
        {"CRJ9", "CSL/Bombardier/CRJ/CRJ-900"},
        {"P28A", "CSL/Piper/PA28/PA28"},
    };
    for (const auto& d : defaults) {
        ModelRule r;
        r.aircraftIcao = QString::fromLatin1(d.icao);
        r.modelPath    = QString::fromLatin1(d.path);
        m_rules.append(r);
    }
    // Airline-specific livery overrides (example)
    auto addAirline = [&](const char* icao, const char* airline, const char* path) {
        ModelRule r;
        r.aircraftIcao = QString::fromLatin1(icao);
        r.airlineIcao  = QString::fromLatin1(airline);
        r.modelPath    = QString::fromLatin1(path);
        r.priority     = 10;
        m_rules.append(r);
    };
    addAirline("B738", "BAW", "CSL/Boeing/B737/B737-800_BAW");
    addAirline("A20N", "EZY", "CSL/Airbus/A320neo/A320neo_EZY");
    addAirline("A20N", "RYR", "CSL/Airbus/A320neo/A320neo_RYR");
    addAirline("A321", "VIR", "CSL/Airbus/A321/A321_VIR");
    addAirline("B789", "BAW", "CSL/Boeing/B787/B787-9_BAW");
}

} // namespace SkyHigh
