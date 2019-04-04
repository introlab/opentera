#ifndef TERA_USER_H_
#define TERA_USER_H_

#include "SharedLib.h"
#include "TeraData.h"

#include <QObject>
#include <QString>
#include <QUuid>
#include <QDateTime>
#include <QJsonValue>

class SHAREDLIB_EXPORT TeraUser : public TeraData
{
    Q_OBJECT
public:
    TeraUser(QObject *parent = nullptr);
    TeraUser(const TeraUser& copy, QObject *parent=nullptr);
    TeraUser(const QJsonValue& json, QObject *parent = nullptr);

    //Getters
    QString     getUserPseudo() const;
    QString     getFirstName() const;
    QString     getLastName() const;
    QString     getEmail() const;
    QUuid       getUuid() const;
    bool        getEnabled() const;
    QString     getNotes() const;
    QString     getProfile() const;
    QDateTime   getLastOnline() const;
    bool        getSuperAdmin() const;

    QString     getName() const;


public Q_SLOTS:

Q_SIGNALS:

protected:

};

#endif
