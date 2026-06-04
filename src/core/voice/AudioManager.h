#pragma once
#include <QObject>
namespace SkyHigh {
class AudioManager : public QObject {
    Q_OBJECT
public:
    explicit AudioManager(QObject* parent = nullptr);
    void setInputDevice(const QString& deviceName);
    void setOutputDevice(const QString& deviceName);
};
}
