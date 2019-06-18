#ifndef TERASESSIONSTATUS_H
#define TERASESSIONSTATUS_H

#include <QObject>

class TeraSessionStatus : public QObject
{
    Q_OBJECT
public:
    enum SessionStatus {
        STATUS_NOTSTARTED = 0,
        STATUS_INPROGRESS = 1,
        STATUS_COMPLETED = 2,
        STATUS_CANCELLED = 3,
        STATUS_TERMINATED = 4
    };

    explicit TeraSessionStatus(QObject *parent = nullptr);

    static QString getStatusName(const SessionStatus& status);
    static QString getStatusName(const int& status);

    static QString getStatusColor(const SessionStatus& status);
    static QString getStatusColor(const int& status);


};

#endif // TERASESSIONSTATUS_H
