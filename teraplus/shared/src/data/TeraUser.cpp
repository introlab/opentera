#include "TeraUser.h"

TeraUser::TeraUser(QObject *parent)
    : TeraData(TERADATA_USER, parent)
{
}

TeraUser::TeraUser(const TeraUser &copy, QObject *parent) : TeraData(TERADATA_USER, parent)
{
    *this = copy;
}

TeraUser::TeraUser(const QJsonValue &json, QObject *parent) :
    TeraData(TERADATA_USER, parent)
{
    fromJson(json);
}

QString TeraUser::getUserPseudo() const
{
    if (hasFieldName("user_username"))
        return getFieldValue("user_profile").toString();

    return QString();
}

QString TeraUser::getFirstName() const
{
    if (hasFieldName("user_firstname"))
        return getFieldValue("user_firstname").toString();

    return QString();
}

QString TeraUser::getLastName() const
{
    if (hasFieldName("user_lastname"))
        return getFieldValue("user_lastname").toString();

    return QString();
}

QString TeraUser::getEmail() const
{
    if (hasFieldName("user_email"))
        return getFieldValue("user_email").toString();

    return QString();
}

QUuid TeraUser::getUuid() const
{
    if (hasFieldName("user_uuid"))
        return getFieldValue("user_uuid").toUuid();

    return QUuid();
}

bool TeraUser::getEnabled() const
{
    if (hasFieldName("user_enabled"))
        return getFieldValue("user_enabled").toBool();

    return false;
}

QString TeraUser::getNotes() const
{
    if (hasFieldName("user_notes"))
        return getFieldValue("user_notes").toString();

    return QString();
}

QString TeraUser::getProfile() const
{
    if (hasFieldName("user_profile"))
        return getFieldValue("user_profile").toString();

    return QString();
}

QDateTime TeraUser::getLastOnline() const
{
    if (hasFieldName("user_lastonline"))
        return getFieldValue("user_lastonline").toDateTime();

    return QDateTime();
}

bool TeraUser::getSuperAdmin() const
{
    if (hasFieldName("user_superadmin"))
        return getFieldValue("user_superadmin").toBool();
    return false;
}

QString TeraUser::getName() const
{
    return getFirstName() + " " + getLastName();
}
