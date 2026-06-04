#pragma once
#include "ISimConnector.h"
namespace SkyHigh {
class MsfsConnector : public ISimConnector {
    Q_OBJECT
public:
    using ISimConnector::ISimConnector;
    void connect() override;
    void disconnect() override;
    bool isConnected() const override;
};
}
