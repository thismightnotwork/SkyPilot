#pragma once
#include <QObject>
namespace SkyHigh {
class ISimConnector : public QObject {
    Q_OBJECT
public:
    using QObject::QObject;
    virtual void connect() = 0;
    virtual void disconnect() = 0;
    virtual bool isConnected() const = 0;
};
}
