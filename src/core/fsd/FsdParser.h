#pragma once
#include "FsdPackets.h"
namespace SkyHigh::Fsd {
struct FsdParser { static ParsedPacket parse(const QString& line); };
}
