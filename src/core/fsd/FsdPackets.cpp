#include "FsdPackets.h"
namespace SkyHigh::Fsd {
TextMessagePacket toTextMessage(const ParsedPacket& packet) {
    TextMessagePacket msg;
    if (packet.fields.size() > 1) msg.from = packet.fields.at(1);
    if (packet.fields.size() > 2) msg.to = packet.fields.at(2);
    if (packet.fields.size() > 3) msg.message = packet.fields.mid(3).join(":");
    return msg;
}
PositionPacket toPositionPacket(const ParsedPacket& packet) {
    PositionPacket pos;
    pos.fastUpdate = packet.raw.startsWith('^');
    if (packet.fields.size() > 1) pos.callsign = packet.fields.at(1);
    if (packet.fields.size() > 2) pos.latitude = packet.fields.at(2).toDouble();
    if (packet.fields.size() > 3) pos.longitude = packet.fields.at(3).toDouble();
    if (packet.fields.size() > 4) pos.altitudeFeet = packet.fields.at(4).toInt();
    if (packet.fields.size() > 5) pos.groundspeed = packet.fields.at(5).toInt();
    if (packet.fields.size() > 6) pos.headingDegrees = packet.fields.at(6).toInt();
    return pos;
}
}
