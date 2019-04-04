#include "TeraData.h"
#include <QDateTime>
#include <Logger.h>

#include <QDebug>


TeraData::TeraData(TeraDataTypes obj_type, QObject *parent) :
    QObject(parent)
{
    setDataType(obj_type);
}

TeraData::TeraData(const TeraData &copy, QObject *parent) : QObject (parent)
{
    *this = copy;
}

TeraData::TeraData(TeraDataTypes obj_type, const QJsonValue &json, QObject *parent):
    QObject(parent)
{
    setDataType(obj_type);
    fromJson(json);
}

int TeraData::getId() const
{
    QVariant raw_id = getFieldValue(m_idField);

    if (raw_id.isValid()){
        return raw_id.toInt();
    }
    return -1;
}

QString TeraData::getName() const
{
    QVariant raw_name = getFieldValue(m_nameField);
    if (raw_name.isValid())
        return raw_name.toString();

    return tr("Inconnu");
}

TeraData &TeraData::operator =(const TeraData &other)
{

    setDataType(other.m_data_type);
    // qDebug() << "Other: " << other.dynamicPropertyNames();

    // qDebug() << "This: " << dynamicPropertyNames();
    for (int i=0; i<other.dynamicPropertyNames().count(); i++){
        //metaObject()->property(i).write(this, other.metaObject()->property(i).read(&other));
        QString name = QString(other.dynamicPropertyNames().at(i));
        // qDebug() << "TeraData::operator= - setting " << name;
        setFieldValue(name, other.property(name.toStdString().c_str()));
    }
    // qDebug() << "This final: " << dynamicPropertyNames();

    return *this;
}

bool TeraData::operator ==(const TeraData &other) const
{
    return getId() == other.getId();
}

TeraDataTypes TeraData::getDataType() const
{
    return m_data_type;
}

bool TeraData::hasFieldName(const QString &fieldName) const
{
    return dynamicPropertyNames().contains(fieldName.toUtf8());
}

QVariant TeraData::getFieldValue(const QString &fieldName) const
{
    if (hasFieldName(fieldName))
        return property(fieldName.toStdString().c_str());

    LOG_WARNING("Field " + fieldName + " not found in " + objectName(), "TeraData::getFieldValue");
    return QVariant();
}

void TeraData::setFieldValue(const QString &fieldName, const QVariant &fieldValue)
{
    setProperty(fieldName.toStdString().c_str(), fieldValue);
}

QList<QString> TeraData::getFieldList() const
{
    QList<QString> rval;
    for (QByteArray fieldname:dynamicPropertyNames()){
        rval.append(QString(fieldname));
    }

    return rval;
}

QString TeraData::getDataTypeName(const TeraDataTypes data_type)
{
    switch (data_type) {
    case TERADATA_USER:
        return "user";
    case TERADATA_SITE:
        return "site";
    case TERADATA_KIT:
        return "kit";
    case TERADATA_SESSIONTYPE:
        return "session_type";
    case TERADATA_TESTDEF:
        return "test_type";
    }

    return "";
}

bool TeraData::hasMetaProperty(const QString &fieldName) const
{
    for (int i=0; i<metaObject()->propertyCount(); i++){
        if (QString(metaObject()->property(i).name()) == fieldName){
            return true;
        }
    }
    return false;
}

void TeraData::setDataType(TeraDataTypes data_type)
{
    m_data_type = data_type;

    // Build default fields - name, ids
    m_objectName = getDataTypeName(m_data_type);
    m_idField = "id_" + m_objectName;
    m_nameField = m_objectName + "_name";


}

bool TeraData::fromJson(const QJsonValue &value)
{
    /*for (int i=0; i<metaObject()->propertyCount(); i++){
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
    }*/
    if (value.isObject()){
        QJsonObject json_object = value.toObject();
        for (int i=0; i<json_object.keys().count(); i++){
            QString fieldName = json_object.keys().at(i);
            //qDebug() << "TeraData::fromJson - setting " << fieldName <<  " to " << json_object[fieldName].toVariant();
            setFieldValue(fieldName, json_object[fieldName].toVariant());
            //setProperty(fieldName.toStdString().c_str(), json_object[fieldName].toVariant());
        }
    }else{
        LOG_WARNING("Trying to load a JSON object which is not an object.", "TeraData::fromJson");
    }

    return true;
}

QJsonObject TeraData::toJson()
{
    QJsonObject object;
    /*for (int i=0; i<metaObject()->propertyCount(); i++){
        QString fieldName = QString(metaObject()->property(i).name());
        if (fieldName != "objectName" && fieldName != "data_type"){
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
    }*/
    for (int i=0; i<dynamicPropertyNames().count(); i++){
        QString fieldName = QString(dynamicPropertyNames().at(i));
        // Ignore "metaObject" properties
        if (!hasMetaProperty(fieldName)){
            QVariant fieldData = getFieldValue(fieldName);
            if (fieldData.canConvert(QMetaType::QString)){
                QDateTime date_tester = QDateTime::fromString(fieldData.toString(), Qt::ISODateWithMs);
                if (date_tester.isValid()){
                    object[fieldName] = fieldData.toDateTime().toString(Qt::ISODateWithMs);
                }else{
                    object[fieldName] = fieldData.toString();
                }
            }else if (fieldData.canConvert(QMetaType::QJsonValue)){
                object[fieldName] = fieldData.toJsonValue();
            }else{
                LOG_WARNING("Field " + fieldName + " can't be 'jsonized'", "TeraData::toJson");
            }
        }
    }
    //qDebug() << object;
    return object;
}
