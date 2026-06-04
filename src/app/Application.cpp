#include "Application.h"
#include <QQmlContext>
#include "ui/viewmodels/ConnectionViewModel.h"

namespace SkyHigh {
Application::Application(int& argc, char** argv) : QGuiApplication(argc, argv) {
    m_engine = std::make_unique<QQmlApplicationEngine>();
    auto* vm = new ConnectionViewModel(m_engine.get());
    m_engine->rootContext()->setContextProperty("connectionViewModel", vm);
    m_engine->load(QUrl("qrc:/src/ui/qml/Main.qml"));
}
}
