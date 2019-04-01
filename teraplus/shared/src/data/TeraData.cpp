#include "TeraData.h"
#include <QDateTime>
#include <Logger.h>

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
        // Skips internal fields
        if (fieldName == "id" || fieldName == "name" || fieldName == "class_name" || fieldName == "objectName")
            continue;
        if (!value[fieldName].isUndefined()){
            if (value[fieldName].isString()){
                QDateTime date_tester = QDateTime::fromString(value[fieldName].toString(), Qt::ISODateWithMs);
                if (date_tester.isValid()){
                    metaObject()->property(i).write(this, date_tester);
                    continue;
                }
                metaObject()->property(i).write(this, value[fieldName].toString());
                continue;
            }
            metaObject()->property(i).write(this, value[fieldName].toVariant());
            continue;
        }
        LOG_WARNING("Field " + fieldName + " not found in JSON.", "TeraData::fromJson");
    }

    return true;
}

QJsonObject TeraData::toJson()
{
    QJsonObject object;
    for (int i=0; i<metaObject()->propertyCount(); i++){
        QString fieldName = QString(metaObject()->property(i).name());
        if (fieldName != "objectName" && fieldName != "class_name"){
            QVariant fieldData =  metaObject()->property(i).read(this);
            if (fieldData.canConvert(QMetaType::QString)){
                QDateTime date_tester = QDateTime::fromString(fieldData.toString(), Qt::ISODateWithMs);
                if (date_tester.isValid()){
                    object[fieldName] = fieldData.toDateTime().toString(Qt::ISODateWithMs);
                }else{
                    object[fieldName] = fieldData.toString();
                }
            }else if (fieldData.canConvert(QMetaType::QJsonValue)){
                object[fieldName] = metaObject()->property(i).read(this).toJsonValue();
            }else{
                LOG_WARNING("Field " + fieldName + " can't be 'jsonized'", "TeraData::toJson");
            }
        }
    }
    return object;
}
