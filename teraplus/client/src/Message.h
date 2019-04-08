#ifndef MESSAGE_H
#define MESSAGE_H

#include <QString>

class Message
{

public:
    typedef enum {
        MESSAGE_NONE,
        MESSAGE_WORKING,
        MESSAGE_OK,
        MESSAGE_WARNING,
        MESSAGE_ERROR}
    MessageType;

    explicit Message();
    explicit Message(const MessageType& msg_type, const QString& msg);

    void setMessage(const MessageType& msg_type, const QString& msg);

    MessageType getMessageType();
    QString getMessageText();

private:
    MessageType m_type;
    QString     m_msg;

};

#endif // MESSAGE_H
