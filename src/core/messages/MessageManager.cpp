#include "MessageManager.h"
namespace SkyHigh {
MessageManager::MessageManager(QObject* parent) : QAbstractListModel(parent) {}
int MessageManager::rowCount(const QModelIndex& parent) const { return parent.isValid() ? 0 : m_messages.size(); }
QVariant MessageManager::data(const QModelIndex& index, int role) const {
    if (!index.isValid() || index.row() < 0 || index.row() >= m_messages.size()) return {};
    const auto& msg = m_messages.at(index.row());
    switch (role) {
        case FromRole: return msg.from; case ToRole: return msg.to; case TextRole: return msg.text; case ChannelRole: return msg.channel;
        case TimestampRole: return msg.timestampUtc.toString(Qt::ISODate); case UnreadRole: return msg.unread; default: return {};
    }
}
QHash<int, QByteArray> MessageManager::roleNames() const {
    return {{FromRole,"from"},{ToRole,"to"},{TextRole,"text"},{ChannelRole,"channel"},{TimestampRole,"timestamp"},{UnreadRole,"unread"}};
}
void MessageManager::appendTextMessage(const SkyHigh::Fsd::TextMessagePacket& packet) {
    beginInsertRows(QModelIndex(), m_messages.size(), m_messages.size());
    MessageEntry entry; entry.from = packet.from; entry.to = packet.to; entry.text = packet.message;
    entry.channel = packet.to.isEmpty() ? QStringLiteral("UNICOM") : packet.to;
    entry.timestampUtc = QDateTime::currentDateTimeUtc(); m_messages.push_back(entry); endInsertRows();
}
void MessageManager::appendSelcal(const QString& from, const QString& code) {
    beginInsertRows(QModelIndex(), m_messages.size(), m_messages.size());
    MessageEntry entry; entry.from = from; entry.text = QString("SELCAL %1").arg(code); entry.channel = QStringLiteral("SELCAL"); entry.timestampUtc = QDateTime::currentDateTimeUtc(); m_messages.push_back(entry); endInsertRows();
}
void MessageManager::markAllRead() { if (m_messages.isEmpty()) return; for (auto& msg : m_messages) msg.unread = false; emit dataChanged(index(0), index(m_messages.size()-1)); }
int MessageManager::unreadCount() const { int count = 0; for (const auto& msg : m_messages) if (msg.unread) ++count; return count; }
}
