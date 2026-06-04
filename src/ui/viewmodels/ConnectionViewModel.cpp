#include "ConnectionViewModel.h"

namespace SkyHigh {

ConnectionViewModel::ConnectionViewModel(QObject* parent) : QObject(parent) {
    connect(&m_manager, &ConnectionManager::statusChanged,        this, &ConnectionViewModel::statusChanged);
    connect(&m_manager, &ConnectionManager::connectedChanged,     this, &ConnectionViewModel::connectedChanged);
    connect(&m_manager, &ConnectionManager::unreadMessagesChanged,this, &ConnectionViewModel::unreadMessagesChanged);
    connect(&m_manager, &ConnectionManager::trafficCountChanged,  this, &ConnectionViewModel::trafficCountChanged);
}

QString  ConnectionViewModel::status()        const { return m_manager.status(); }
bool     ConnectionViewModel::connected()     const { return m_manager.connected(); }
QObject* ConnectionViewModel::messagesModel() const { return const_cast<ConnectionManager&>(m_manager).messagesModel(); }
QObject* ConnectionViewModel::trafficModel()  const { return const_cast<ConnectionManager&>(m_manager).trafficModel(); }
int      ConnectionViewModel::unreadMessages()const { return m_manager.unreadMessages(); }
int      ConnectionViewModel::trafficCount()  const { return m_manager.trafficCount(); }

void ConnectionViewModel::connectOrDisconnect() {
    if (m_manager.connected())
        m_manager.disconnectPilot();
    else
        m_manager.connectPilot(m_callsign, m_cid, m_password);
}

void ConnectionViewModel::sendMessage(const QString& channel, const QString& text) {
    m_manager.sendTextMessage(channel, text);
}

} // namespace SkyHigh
