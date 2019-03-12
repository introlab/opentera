#include "TeraData.h"
#include <QDateTime>
#include <QDebug>

TeraData::TeraData(QObject *parent) : QObject(parent)
{

}

TeraData::TeraData(const TeraData &copy, QObject *parent) : QObject (parent)
{
    *this = copy;
}

TeraData::TeraData(const QJsonValue &json, QObject *parent): QObject(parent)
{
    fromJson(json);
}

void TeraData::setId(int id)
{
    if (m_id == id)
        return;

    m_id = id;
    emit idChanged();
}
void TeraData::setName(QString name)
{
    if (m_name == name)
        return;

    m_name = name;
    emit nameChanged(m_name);
}

int TeraData::getId() const
{
    return m_id;
}

QString TeraData::getName() const
{
    return m_name;
}

TeraData &TeraData::operator =(const TeraData &other)
{
    /*m_id = other.m_id;
    m_name = other.m_name;*/
    for (int i=0; i<metaObject()->propertyCount(); i++){
        metaObject()->property(i).write(this, other.metaObject()->property(i).read(&other));
    }

    return *this;
}

bool TeraData::operator ==(const TeraData &other) const
{
    return m_id == other.m_id;
}

QString TeraData::getClassName() const
{
    return metaObject()->className();
}

bool TeraData::fromJson(const QJsonValue &value)
{
    for (int i=0; i<metaObject()->propertyCount(); i++){
        QString fieldName = QString(metaObject()->property(i).name());
        if (!value[fieldName].isUndefined()){
            if (value[fieldName].isString()){
                QDateTime date_tester = QDateTime::fromString(value[fieldName].toString(), Qt::ISODateWithMs);
                if (date_tester.isValid()){
                    metaObject()->property(i).write(this, date_tester);
                    continue;
                }
            }
            metaObject()->property(i).write(this, value[fieldName].toVariant());
        }
    }

    return true;
}

QJsonObject TeraData::toJson()
{
    QJsonObject object;
    for (int i=0; i<metaObject()->propertyCount(); i++){
        QString fieldName = QString(metaObject()->property(i).name());
        if (fieldName != "objectName"){
            if (metaObject()->property(i).read(this).canConvert(QMetaType::QDateTime)){
                object[fieldName] = metaObject()->property(i).read(this).toDateTime().toString(Qt::ISODateWithMs);
            }else{
                object[fieldName] = metaObject()->property(i).read(this).toJsonValue();
            }
        }
    }
    return object;
}
