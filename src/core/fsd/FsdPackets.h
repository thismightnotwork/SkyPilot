#pragma once
#include <QString>
#include <QStringList>

namespace SkyHigh::Fsd {
struct TextMessagePacket { QString from; QString to; QString message; };
struct PositionPacket {
    QString callsign;
    double latitude{0.0};
    double longitude{0.0};
    int altitudeFeet{0};
    int groundspeed{0};
    int headingDegrees{0};
    bool fastUpdate{false};
};
enum class PacketType {
    Unknown, ServerIdent, TextMessage, Ping, Pong, AddPilot, AddAtc, FlightPlan,
    Position, PilotConfig, DeleteClient, ClientQuery, ClientResponse, Selcal
};
struct ParsedPacket { PacketType type{PacketType::Unknown}; QString raw; QStringList fields; };
TextMessagePacket toTextMessage(const ParsedPacket& packet);
PositionPacket toPositionPacket(const ParsedPacket& packet);
}
