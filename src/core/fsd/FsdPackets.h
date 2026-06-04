#pragma once
#include <QString>
#include "FsdParser.h"

namespace SkyHigh::Fsd {

/// Decoded position update from a @ or ^ packet.
struct PositionPacket {
    QString callsign;
    double  latitude{0.0};
    double  longitude{0.0};
    int     altitudeFeet{0};
    int     headingDegrees{0};
    int     groundspeed{0};
    int     verticalSpeed{0};
    bool    onGround{false};
    bool    isFastUpdate{false};  // true if ^ packet
    QString aircraftIcao;
    QString airlineIcao;
};

/// Decoded text message from a #TM packet.
struct TextMessagePacket {
    QString from;
    QString to;
    QString message;
};

/// Convert a parsed position packet.
inline PositionPacket toPositionPacket(const ParsedPacket& p) {
    PositionPacket r;
    // Field layout: mode:callsign:squawk:rating:lat:lon:altTrue:gs:pbhFlags:miscFlags
    if (p.fields.size() < 8) return r;
    r.isFastUpdate     = p.fields.at(0).startsWith('^');
    r.callsign         = p.fields.at(1);
    r.latitude         = p.fields.at(4).toDouble();
    r.longitude        = p.fields.at(5).toDouble();
    r.altitudeFeet     = p.fields.at(6).toInt();
    r.groundspeed      = p.fields.at(7).toInt();
    // PBH flags field [8] encodes pitch/bank/heading packed as uint32
    if (p.fields.size() > 8) {
        const quint32 pbh = p.fields.at(8).toUInt();
        r.headingDegrees = static_cast<int>((pbh & 0x3FF) * 360.0 / 1024.0);
    }
    if (p.fields.size() > 9) {
        const int flags = p.fields.at(9).toInt();
        r.onGround = (flags & 0x2) != 0;
    }
    return r;
}

/// Convert a parsed #TM packet.
inline TextMessagePacket toTextMessage(const ParsedPacket& p) {
    TextMessagePacket r;
    // #TMfrom:to:message
    if (p.fields.size() < 3) return r;
    r.from    = p.fields.at(0).mid(3); // strip #TM prefix
    r.to      = p.fields.at(1);
    r.message = p.fields.mid(2).join(':'); // message may contain colons
    return r;
}

} // namespace SkyHigh::Fsd
