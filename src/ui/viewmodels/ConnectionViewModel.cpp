#include "ConnectionViewModel.h"

namespace SkyHigh {

ConnectionViewModel::ConnectionViewModel(QObject* parent) : QObject(parent) {
    connect(&m_manager, &ConnectionManager::statusChanged,         this, &ConnectionViewModel::statusChanged);
    connect(&m_manager, &ConnectionManager::connectedChanged,      this, &ConnectionViewModel::connectedChanged);
    connect(&m_manager, &ConnectionManager::unreadMessagesChanged, this, &ConnectionViewModel::unreadMessagesChanged);
    connect(&m_manager, &ConnectionManager::trafficCountChanged,   this, &ConnectionViewModel::trafficCountChanged);
}

QString  ConnectionViewModel::status()        const { return m_manager.status(); }
bool     ConnectionViewModel::connected()     const { return m_manager.connected(); }
QObject* ConnectionViewModel::messagesModel() const { return const_cast<ConnectionManager&>(m_manager).messagesModel(); }
QObject* ConnectionViewModel::trafficModel()  const { return const_cast<ConnectionManager&>(m_manager).trafficModel(); }
int      ConnectionViewModel::unreadMessages()const { return m_manager.unreadMessages(); }
int      ConnectionViewModel::trafficCount()  const { return m_manager.trafficCount(); }

QString ConnectionViewModel::ownPositionText() const {
    return QString("Lat %1  Lon %2  Alt %3ft  Hdg %4°  GS %5kt")
        .arg(m_ownData.latitude,  0, 'f', 4)
        .arg(m_ownData.longitude, 0, 'f', 4)
        .arg(m_ownData.altitudeFeet)
        .arg(m_ownData.headingDegrees)
        .arg(m_ownData.groundspeedKts);
}

void ConnectionViewModel::connectOrDisconnect() {
    if (m_manager.connected())
        m_manager.disconnectPilot();
    else
        m_manager.connectPilot(m_callsign, m_cid, m_password);
}

void ConnectionViewModel::sendMessage(const QString& channel, const QString& text) {
    m_manager.sendTextMessage(channel, text);
}

void ConnectionViewModel::setSimType(int index) {
    detachSimConnector();
    switch (index) {
        case 0: attachSimConnector(&m_msfsConnector);   break;
        case 1: attachSimConnector(&m_xplaneConnector); break;
        default: m_simStatus = "No simulator"; emit simStatusChanged(); break;
    }
}

void ConnectionViewModel::attachSimConnector(ISimConnector* connector) {
    m_activeConnector = connector;
    connect(connector, &ISimConnector::simConnected, this, [this]() {
        m_simConnected = true;
        emit simConnectedChanged();
    });
    connect(connector, &ISimConnector::simDisconnected, this, [this]() {
        m_simConnected = false;
        emit simConnectedChanged();
    });
    connect(connector, &ISimConnector::statusMessage, this, [this](const QString& msg) {
        m_simStatus = msg;
        emit simStatusChanged();
    });
    connect(connector, &ISimConnector::positionUpdated, this, [this](const OwnAircraftData& data) {
        m_ownData = data;
        m_manager.updateOwnPosition(data.latitude, data.longitude,
                                     data.altitudeFeet, data.headingDegrees, data.groundspeedKts);
        emit ownPositionChanged();
    });
    connector->start();
}

void ConnectionViewModel::detachSimConnector() {
    if (m_activeConnector) {
        m_activeConnector->stop();
        m_activeConnector->disconnect(this);
        m_activeConnector = nullptr;
        m_simConnected = false;
        emit simConnectedChanged();
    }
}

} // namespace SkyHigh
