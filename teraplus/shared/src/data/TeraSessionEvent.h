#ifndef TERASESSIONEVENT_H
#define TERASESSIONEVENT_H

#include <QObject>

class TeraSessionEvent : public QObject
{
    Q_OBJECT
public:
    explicit TeraSessionEvent(QObject *parent = nullptr);

    enum SessionEventType {
        GENERAL_ERROR = 0,
        GENERAL_INFO = 1,
        GENERAL_WARNING = 2,
        SESSION_START = 3,
        SESSION_STOP = 4,
        DEVICE_ON_CHARGE = 5,
        DEVICE_OFF_CHARGE = 6,
        DEVICE_LOW_BATT = 7,
        DEVICE_STORAGE_LOW = 8,
        DEVICE_STORAGE_FULL = 9,
        DEVICE_EVENT = 10,
        USER_EVENT = 11
    };

    static QString getEventTypeName(const SessionEventType& event);
    static QString getEventTypeName(const int& event);

    static QString getIconFilenameForEventType(const SessionEventType& event);
    static QString getIconFilenameForEventType(const int& event);

signals:

public slots:
};

#endif // TERASESSIONEVENT_H
