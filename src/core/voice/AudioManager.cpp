#include "AudioManager.h"
namespace SkyHigh {
AudioManager::AudioManager(QObject* parent) : QObject(parent) {}
void AudioManager::setInputDevice(const QString& deviceName) { Q_UNUSED(deviceName); }
void AudioManager::setOutputDevice(const QString& deviceName) { Q_UNUSED(deviceName); }
}
