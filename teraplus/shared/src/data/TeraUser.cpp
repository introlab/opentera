#include "TeraUser.h"

TeraUser::TeraUser(QObject *parent)
    : TeraData(parent)
{
    m_superadmin = false;
}

TeraUser::TeraUser(const TeraUser &copy, QObject *parent) : TeraData(parent)
{
    *this = copy;
}

TeraUser::TeraUser(const QJsonValue &json, QObject *parent) : TeraData(parent)
{
    fromJson(json);
}

QString TeraUser::getUserPseudo() const
{
    return m_userPseudo;
}

QString TeraUser::getFirstName() const
{
    return m_firstName;
}

QString TeraUser::getLastName() const
{
    return m_lastName;
}

QString TeraUser::getEmail() const
{
    return m_email;
}

UserType TeraUser::getUserType() const
{
    return m_userType;
}

QUuid TeraUser::getUuid() const
{
    return m_uuid;
}

bool TeraUser::getEnabled() const
{
    return m_enabled;
}

QString TeraUser::getNotes() const
{
    return m_notes;
}

QString TeraUser::getProfile() const
{
    return m_profile;
}

QDateTime TeraUser::getLastOnline() const
{
    return m_lastonline;
}

bool TeraUser::getSuperAdmin() const
{
    return m_superadmin;
}

QString TeraUser::getName() const
{
    return m_firstName + " " + m_lastName;
}


QJsonObject TeraUser::toJson()
{
    QJsonObject json = TeraData::toJson();

    json.remove("id");
    json["user_lastonline"] = m_lastonline.toString();

    return json;
}

void TeraUser::setUserPseudo(const QString &pseudo)
{
    if (m_userPseudo==pseudo)
        return;

    m_userPseudo = pseudo;
    emit userPseudoChanged(m_userPseudo);
}

void TeraUser::setFirstName(const QString &firstName)
{
    if (m_firstName==firstName)
        return;

    m_firstName = firstName;
    emit firstNameChanged(m_firstName);
}

void TeraUser::setLastName(const QString &lastName)
{
    if (m_lastName==lastName)
        return;

    m_lastName = lastName;
    emit lastNameChanged(m_lastName);
}

void TeraUser::setEmail(const QString &email)
{
    if (m_email==email)
        return;
    m_email = email;
    emit emailChanged(m_email);
}

void TeraUser::setUserType(const UserType type)
{
    if (m_userType==type)
        return;

    m_userType = type;
    emit userTypeChanged(m_userType);
}

void TeraUser::setUuid(const QUuid &uuid)
{
    if (m_uuid == uuid)
        return;

    m_uuid = uuid;
    emit uuidChanged(m_uuid);
}

void TeraUser::setEnabled(const bool &enabled)
{
    if (m_enabled == enabled)
        return;

    m_enabled = enabled;
    emit enabledChanged(m_enabled);
}

void TeraUser::setNotes(const QString &notes)
{
    if (m_notes == notes)
        return;

    m_notes = notes;
    emit notesChanged(m_notes);
}

void TeraUser::setProfile(const QString &profile)
{
    if (m_profile == profile)
        return;

    m_profile = profile;
    emit profileChanged(m_profile);
}

void TeraUser::setLastOnline(const QDateTime &last_online)
{
    if (m_lastonline == last_online)
        return;

    m_lastonline = last_online;
    emit lastOnlineChanged(last_online);
}

void TeraUser::setSuperAdmin(const bool &super)
{
    if (m_superadmin==super)
        return;

    m_superadmin = super;
    emit superAdminChanged(super);
}
