#ifndef TERA_USER_H_
#define TERA_USER_H_

#include "SharedLib.h"
#include "TeraData.h"

#include <QObject>
#include <QString>
#include <QUuid>
#include <QDateTime>
#include <QJsonValue>

enum UserType{
    TERA_USERTYPE_NORMAL=1,
    TERA_USERTYPE_KIT=2,
    TERA_USERTYPE_ROBOT=3
};

Q_DECLARE_METATYPE(UserType)

class SHAREDLIB_EXPORT TeraUser : public TeraData
{
    Q_OBJECT

    Q_PROPERTY(int id_user READ getId WRITE setId NOTIFY idChanged)
    Q_PROPERTY(QString user_username READ getUserPseudo WRITE setUserPseudo NOTIFY userPseudoChanged)
    Q_PROPERTY(QString user_firstname READ getFirstName WRITE setFirstName NOTIFY firstNameChanged)
    Q_PROPERTY(QString user_lastname READ getLastName WRITE setLastName NOTIFY lastNameChanged)
    Q_PROPERTY(QString user_email READ getEmail WRITE setEmail NOTIFY emailChanged)
    Q_PROPERTY(UserType user_type READ getUserType WRITE setUserType NOTIFY userTypeChanged)
    Q_PROPERTY(QUuid user_uuid READ getUuid WRITE setUuid NOTIFY uuidChanged)
    Q_PROPERTY(bool user_enabled READ getEnabled WRITE setEnabled NOTIFY enabledChanged)
    Q_PROPERTY(QString user_notes READ getNotes WRITE setNotes NOTIFY notesChanged)
    Q_PROPERTY(QString user_profile READ getProfile WRITE setProfile NOTIFY profileChanged)
    Q_PROPERTY(QDateTime user_lastonline READ getLastOnline WRITE setLastOnline NOTIFY lastOnlineChanged)
    Q_PROPERTY(bool user_superadmin READ getSuperAdmin WRITE setSuperAdmin NOTIFY superAdminChanged)

public:




    TeraUser(QObject *parent = nullptr);
    TeraUser(const TeraUser& copy, QObject *parent=nullptr);
    TeraUser(const QString &pseudo, const QString &firstName, const QString &lastName, const QString &email, UserType type, const QUuid &uuid,
             const bool &enabled, const QString &notes, const QString &profile, const QDateTime &last_online, const bool &superadmin, QObject *parent=nullptr)
        :   TeraData(parent),
          m_userPseudo(pseudo),
          m_firstName(firstName),
          m_lastName(lastName),
          m_email(email),
          m_userType(type),
          m_uuid(uuid),
          m_enabled(enabled),
          m_notes(notes),
          m_profile(profile),
          m_lastonline(last_online),
          m_superadmin(superadmin)
    {

    }

    TeraUser(const QJsonValue& json, QObject *parent = nullptr);

    //Getters
    QString     getUserPseudo() const;
    QString     getFirstName() const;
    QString     getLastName() const;
    QString     getEmail() const;
    UserType    getUserType() const;
    QUuid       getUuid() const;
    bool        getEnabled() const;
    QString     getNotes() const;
    QString     getProfile() const;
    QDateTime   getLastOnline() const;
    bool        getSuperAdmin() const;

    QString     getName() const;

    // Utils
    QJsonObject toJson();

public Q_SLOTS:

    //Setters
    void setUserPseudo(const QString &pseudo);
    void setFirstName(const QString &firstName);
    void setLastName(const QString &lastName);
    void setEmail(const QString &email);
    void setUserType(const UserType type);
    void setUuid(const QUuid &uuid);
    void setEnabled(const bool &enabled);
    void setNotes(const QString &notes);
    void setProfile(const QString &profile);
    void setLastOnline(const QDateTime &last_online);
    void setSuperAdmin(const bool &super);

Q_SIGNALS:
    void userPseudoChanged(QString pseudo);
    void firstNameChanged(QString firstName);
    void lastNameChanged(QString lastName);
    void emailChanged(QString email);
    void userTypeChanged(UserType type);
    void uuidChanged(QUuid uuid);
    void enabledChanged(bool enabled);
    void notesChanged(QString notes);
    void profileChanged(QString profile);
    void lastOnlineChanged(QDateTime last_online);
    void superAdminChanged(bool super);

protected:

    QString     m_userPseudo;
    QString     m_firstName;
    QString     m_lastName;
    QString     m_email;
    UserType    m_userType;
    QUuid       m_uuid;
    bool        m_enabled;
    QString     m_notes;
    QString     m_profile;
    QDateTime   m_lastonline;
    bool        m_superadmin;

};

#endif
