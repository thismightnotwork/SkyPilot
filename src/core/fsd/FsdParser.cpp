#include "FsdParser.h"

namespace SkyHigh::Fsd {

ParsedPacket FsdParser::parse(const QString& line) {
    ParsedPacket packet;
    packet.raw = line;

    // Position packets use @ or ^ as the very first character, not a colon-delimited prefix
    if (line.startsWith('@') || line.startsWith('^')) {
        packet.type   = PacketType::Position;
        packet.fields = line.split(':');
        if (!packet.fields.isEmpty()) {
            // Strip the leading @ or ^ from the mode field, extract callsign from field[1]
            packet.fields[0] = packet.fields[0].mid(1);
        }
        return packet;
    }

    packet.fields = line.split(':');
    const QString prefix = packet.fields.isEmpty() ? QString() : packet.fields.at(0);

    if      (prefix == QStringLiteral("$DI")) packet.type = PacketType::ServerIdent;
    else if (prefix == QStringLiteral("#TM")) packet.type = PacketType::TextMessage;
    else if (prefix == QStringLiteral("$PI")) packet.type = PacketType::Ping;
    else if (prefix == QStringLiteral("$PO")) packet.type = PacketType::Pong;
    else if (prefix == QStringLiteral("#AP")) packet.type = PacketType::AddPilot;
    else if (prefix == QStringLiteral("#AA")) packet.type = PacketType::AddAtc;
    else if (prefix == QStringLiteral("$FP")) packet.type = PacketType::FlightPlan;
    else if (prefix == QStringLiteral("#SB")) packet.type = PacketType::PilotConfig;
    else if (prefix == QStringLiteral("#DP")) packet.type = PacketType::DeleteClient;
    else if (prefix == QStringLiteral("$CQ")) packet.type = PacketType::ClientQuery;
    else if (prefix == QStringLiteral("$CR")) packet.type = PacketType::ClientResponse;
    else if (prefix == QStringLiteral("#SC")) packet.type = PacketType::Selcal;
    else                                       packet.type = PacketType::Unknown;

    return packet;
}

} // namespace SkyHigh::Fsd
