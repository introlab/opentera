#include "Message.h"

Message::Message()
{

}

Message::Message(const Message::MessageType &msg_type, const QString &msg)
{
    setMessage(msg_type, msg);
}

void Message::setMessage(const Message::MessageType &msg_type, const QString &msg)
{
    m_msg = msg;
    m_type = msg_type;
}

Message::MessageType Message::getMessageType()
{
    return m_type;
}

QString Message::getMessageText()
{
    return m_msg;
}
