#pragma once
#include <QAbstractListModel>
#include <QDateTime>
#include "core/fsd/FsdPackets.h"
namespace SkyHigh {
struct MessageEntry { QString from; QString to; QString text; QString channel; QDateTime timestampUtc; bool unread{true}; };
class MessageManager : public QAbstractListModel {
    Q_OBJECT
public:
    enum Roles { FromRole = Qt::UserRole + 1, ToRole, TextRole, ChannelRole, TimestampRole, UnreadRole };
    explicit MessageManager(QObject* parent = nullptr);
    int rowCount(const QModelIndex& parent = QModelIndex()) const override;
    QVariant data(const QModelIndex& index, int role = Qt::DisplayRole) const override;
    QHash<int, QByteArray> roleNames() const override;
    void appendTextMessage(const SkyHigh::Fsd::TextMessagePacket& packet);
    void appendSelcal(const QString& from, const QString& code);
    void markAllRead();
    int unreadCount() const;
private:
    QList<MessageEntry> m_messages;
};
}
