#pragma once
#include <QObject>
namespace SkyHigh {
class MainWindow : public QObject {
    Q_OBJECT
public:
    explicit MainWindow(QObject* parent = nullptr);
};
}
