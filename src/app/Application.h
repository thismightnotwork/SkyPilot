#pragma once
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <memory>

namespace SkyHigh {
class Application : public QGuiApplication {
    Q_OBJECT
public:
    Application(int& argc, char** argv);
private:
    std::unique_ptr<QQmlApplicationEngine> m_engine;
};
}
