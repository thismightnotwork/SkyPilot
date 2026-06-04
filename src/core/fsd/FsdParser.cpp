#include "FsdParser.h"
namespace SkyHigh::Fsd {
ParsedPacket FsdParser::parse(const QString& line) {
    ParsedPacket packet;
    packet.raw = line;
    packet.fields = line.split(':');
    const QString prefix = packet.fields.isEmpty() ? QString() : packet.fields.at(0);
    if (prefix == QStringLiteral("$DI"))     packet.type = PacketType::ServerIdent;
    else if (prefix == QStringLiteral("#TM")) packet.type = PacketType::TextMessage;
    else if (prefix == QStringLiteral("$PI")) packet.type = PacketType::Ping;
    else if (prefix == QStringLiteral("$PO")) packet.type = PacketType::Pong;
    else if (prefix == QStringLiteral("#AP")) packet.type = PacketType::AddPilot;
    else if (prefix == QStringLiteral("#AA")) packet.type = PacketType::AddAtc;
    else if (prefix == QStringLiteral("$FP")) packet.type = PacketType::FlightPlan;
    else if (prefix == QStringLiteral("@") || line.startsWith('@') || line.startsWith('^')) packet.type = PacketType::Position;
    else if (prefix == QStringLiteral("#SB")) packet.type = PacketType::PilotConfig;
    else if (prefix == QStringLiteral("#DP")) packet.type = PacketType::DeleteClient;
    else if (prefix == QStringLiteral("$CQ")) packet.type = PacketType::ClientQuery;
    else if (prefix == QStringLiteral("$CR")) packet.type = PacketType::ClientResponse;
    else if (prefix == QStringLiteral("#SC")) packet.type = PacketType::Selcal;
    return packet;
}
}
