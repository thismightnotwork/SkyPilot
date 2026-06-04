#include <QtTest>
#include "core/fsd/FsdProtocol.h"
using namespace SkyHigh::Fsd;
class TestFsdProtocol : public QObject {
    Q_OBJECT
private slots:
    void testBuildTextMessage() {
        FsdProtocol p;
        const QString line = p.buildTextMessage("SKY123", "ATC_EGKK", "Request startup");
        QVERIFY(line.startsWith("#TM"));
        QVERIFY(line.contains("SKY123"));
        QVERIFY(line.contains("ATC_EGKK"));
        QVERIFY(line.contains("Request startup"));
    }
    void testBuildAddPilot() {
        FsdProtocol p;
        ConnectRequest req; req.callsign = "SKY123"; req.password = "hunter2"; req.realName = "Test Pilot";
        const QString line = p.buildAddPilot(req);
        QVERIFY(line.startsWith("#AP"));
        QVERIFY(line.contains("SKY123"));
    }
};
QTEST_MAIN(TestFsdProtocol)
#include "test_fsd_protocol.moc"
