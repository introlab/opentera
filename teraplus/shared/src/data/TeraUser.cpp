#include "TeraUser.h"

TeraUser::TeraUser(QObject *parent)
    : QObject(parent)
{

}

QString TeraUser::getUserPseudo()
{
    return m_userPseudo;
}

QString TeraUser::getFirstName()
{
    return m_firstName;
}

QString TeraUser::getLastName()
{
    return m_lastName;
}

QString TeraUser::getEmail()
{
    return m_email;
}

TeraUser::UserType TeraUser::getUserType()
{
    return m_userType;
}

QUuid TeraUser::getUuid()
{
    return m_uuid;
}

bool TeraUser::getEnabled()
{
    return m_enabled;
}

QString TeraUser::getNotes()
{
    return m_notes;
}

QString TeraUser::getProfile()
{
    return m_profile;
}

QDateTime TeraUser::getLastOnline()
{
    return m_lastonline;
}

bool TeraUser::getSuperAdmin()
{
    return m_superadmin;
}

void TeraUser::setUserPseudo(const QString &pseudo)
{
    m_userPseudo = pseudo;
    emit userPseudoChanged(m_userPseudo);
}

void TeraUser::setFirstName(const QString &firstName)
{
    m_firstName = firstName;
    emit firstNameChanged(m_firstName);
}

void TeraUser::setLastName(const QString &lastName)
{
    m_lastName = lastName;
    emit lastNameChanged(m_lastName);
}

void TeraUser::setEmail(const QString &email)
{
    m_email = email;
    emit emailChanged(m_email);
}

void TeraUser::setUserType(const TeraUser::UserType type)
{
    m_userType = type;
    emit userTypeChanged(m_userType);
}

void TeraUser::setUuid(const QUuid &uuid)
{
    m_uuid = uuid;
    emit uuidChanged(m_uuid);
}

void TeraUser::setEnabled(const bool &enabled)
{
    m_enabled = enabled;
    emit enabledChanged(m_enabled);
}

void TeraUser::setNotes(const QString &notes)
{
    m_notes = notes;
    emit notesChanged(m_notes);
}

void TeraUser::setProfile(const QString &profile)
{
    m_profile = profile;
    emit profileChanged(m_profile);
}

void TeraUser::setLastOnline(const QDateTime &last_online)
{
    m_lastonline = last_online;
    emit lastOnlineChanged(last_online);
}

void TeraUser::setSuperAdmin(const bool &super)
{
    m_superadmin = super;
    emit superAdminChanged(super);
}
