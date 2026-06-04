#pragma once
#include <QString>

namespace SkyHigh::Config {
    // ── FSD Server ────────────────────────────────────────────────────────────
    // Replace the placeholder with your actual FSD server hostname/IP.
    inline const QString FSD_SERVER_HOST = QStringLiteral("fsd.YOUR-DOMAIN.com"); // <-- SET THIS
    inline const quint16  FSD_SERVER_PORT = 6809;

    // ── Mumble Voice Server ───────────────────────────────────────────────────
    // Replace the placeholder with your Mumble/FGCom-Mumble server hostname/IP.
    inline const QString MUMBLE_SERVER_HOST = QStringLiteral("voice.YOUR-DOMAIN.com"); // <-- SET THIS
    inline const quint16  MUMBLE_SERVER_PORT = 64738;

    // ── Application ───────────────────────────────────────────────────────────
    inline const QString APP_NAME    = QStringLiteral("SkyHigh Pilot");
    inline const QString APP_VERSION = QStringLiteral("1.0.0");
    inline const QString CLIENT_ID   = QStringLiteral("SKYHIGH");
}
