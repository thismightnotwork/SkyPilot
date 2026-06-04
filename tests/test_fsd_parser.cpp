#include <QtTest>
#include "core/fsd/FsdParser.h"
using namespace SkyHigh::Fsd;
class TestFsdParser : public QObject {
    Q_OBJECT
private slots:
    void testTextMessage() {
        const auto p = FsdParser::parse("#TMATC_EGKK:SKY123:Cleared ILS 26L");
        QCOMPARE(p.type, PacketType::TextMessage);
        QCOMPARE(p.fields.at(1), QStringLiteral("ATC_EGKK"));
    }
    void testPositionPacket() {
        const auto p = FsdParser::parse("@N:SKY123:51.148:-0.190:28000:450:270:0");
        QCOMPARE(p.type, PacketType::Position);
    }
};
QTEST_MAIN(TestFsdParser)
#include "test_fsd_parser.moc"
