#include "TeraData.h"
#include <QDateTime>
#include <Logger.h>

#include <QDebug>

/*
TeraData::TeraData(QObject *parent) :
    QObject(parent)
{
    setDataType(TERADATA_NONE);
}*/

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

QString TeraData::getIdFieldName() const
{
    return m_idField;
}

void TeraData::setId(const int &id)
{
    setFieldValue(m_idField, id);
}

QString TeraData::getName() const
{
    QVariant raw_name = getFieldValue(m_nameField);
    if (raw_name.isValid())
        return raw_name.toString();

    return tr("Inconnu");
}

void TeraData::setName(const QString &name)
{
    setFieldValue(m_nameField, name);
}

bool TeraData::isNew()
{
    return getId()<=0;
}

TeraData &TeraData::operator =(const TeraData &other)
{

    setDataType(other.m_data_type);
    // qDebug() << "Other: " << other.dynamicPropertyNames();

    // qDebug() << "This: " << dynamicPropertyNames();
    /*for (int i=0; i<other.dynamicPropertyNames().count(); i++){
        //metaObject()->property(i).write(this, other.metaObject()->property(i).read(&other));
        QString name = QString(other.dynamicPropertyNames().at(i));
        // qDebug() << "TeraData::operator= - setting " << name;
        setFieldValue(name, other.property(name.toStdString().c_str()));
    }*/
    // qDebug() << "This final: " << dynamicPropertyNames();

    m_fieldsValue = other.m_fieldsValue;

    return *this;
}

bool TeraData::operator ==(const TeraData &other) const
{
    return getId() == other.getId() && getDataType() == other.getDataType();
}

TeraDataTypes TeraData::getDataType() const
{
    return m_data_type;
}

bool TeraData::hasFieldName(const QString &fieldName) const
{
    //return dynamicPropertyNames().contains(fieldName.toUtf8());
    return m_fieldsValue.contains(fieldName);
}

void TeraData::removeFieldName(const QString &fieldName)
{
    if (m_fieldsValue.contains(fieldName)){
        m_fieldsValue.remove(fieldName);
    }
}

QVariant TeraData::getFieldValue(const QString &fieldName) const
{
    if (hasFieldName(fieldName))
        //return property(fieldName.toStdString().c_str());
        return m_fieldsValue[fieldName];

    LOG_WARNING("Field " + fieldName + " not found in " + metaObject()->className(), "TeraData::getFieldValue");
    return QVariant();
}

void TeraData::setFieldValue(const QString &fieldName, const QVariant &fieldValue)
{
    //setProperty(fieldName.toStdString().c_str(), fieldValue);
    m_fieldsValue[fieldName] = fieldValue;
}

QList<QString> TeraData::getFieldList() const
{
    QList<QString> rval;
    //for (QByteArray fieldname:dynamicPropertyNames()){
    for (QString fieldname:m_fieldsValue.keys()){
        rval.append(fieldname);
    }

    return rval;
}

QString TeraData::getDataTypeName(const TeraDataTypes &data_type)
{
    switch (data_type) {
    case TERADATA_NONE:
        return "";
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
    case TERADATA_PROJECT:
        return "project";
    case TERADATA_DEVICE:
        return "device";
    case TERADATA_PARTICIPANT:
        return "participant";
    case TERADATA_GROUP:
        return "participantgroup";
    case TERADATA_SITEACCESS:
        return "siteaccess";
    case TERADATA_KITDEVICE:
        return "kit_device";
    }

    return "";
}

TeraDataTypes TeraData::getDataTypeFromPath(const QString &path)
{
    if (path==WEB_USERINFO_PATH)            return TERADATA_USER;
    if (path==WEB_SITEINFO_PATH)            return TERADATA_SITE;
    if (path==WEB_PROJECTINFO_PATH)         return TERADATA_PROJECT;
    if (path==WEB_SITEACCESS_PATH)          return TERADATA_SITEACCESS;
    if (path==WEB_KITINFO_PATH)             return TERADATA_KIT;
    if (path==WEB_DEVICEINFO_PATH)          return TERADATA_DEVICE;
    if (path==WEB_KITDEVICE_PATH)           return TERADATA_KITDEVICE;
    if (path==WEB_PARTICIPANTINFO_PATH)     return TERADATA_PARTICIPANT;

    LOG_ERROR("Unknown data type for path: " + path, "TeraData::getDataTypeFromPath");

    return TERADATA_NONE;
}

QString TeraData::getPathForDataType(const TeraDataTypes &data_type)
{
    if (data_type==TERADATA_USER)           return WEB_USERINFO_PATH;
    if (data_type==TERADATA_SITE)           return WEB_SITEINFO_PATH;
    if (data_type==TERADATA_PROJECT)        return WEB_PROJECTINFO_PATH;
    if (data_type==TERADATA_DEVICE)         return WEB_DEVICEINFO_PATH;
    if (data_type==TERADATA_KITDEVICE)      return WEB_KITDEVICE_PATH;
    if (data_type==TERADATA_KIT)            return WEB_KITINFO_PATH;
    if (data_type==TERADATA_PARTICIPANT)    return WEB_PARTICIPANTINFO_PATH;

    LOG_ERROR("Unknown path for data_type: " + getDataTypeName(data_type), "TeraData::getPathForDataType");

    return QString();
}

QString TeraData::getIconFilenameForDataType(const TeraDataTypes &data_type)
{
    switch(data_type){
    case TERADATA_USER:
        return "://icons/software_user.png";
    case TERADATA_SITE:
        return "://icons/site.png";
    case TERADATA_KIT:
        return "://icons/kit.png";
    case TERADATA_SESSIONTYPE:
        return "://icons/session.png";
    case TERADATA_TESTDEF:
        return "://icons/test.png";
    case TERADATA_DEVICE:
        return "://icons/device.png";
    case TERADATA_PARTICIPANT:
        return "://icons/patient.png";
    case TERADATA_GROUP:
        return "://icons/group.png";
    case TERADATA_PROJECT:
        return "://icons/project.png";
    default:
        return "://icons/error.png";
    }

}
/*
bool TeraData::hasMetaProperty(const QString &fieldName) const
{
    for (int i=0; i<metaObject()->propertyCount(); i++){
        if (QString(metaObject()->property(i).name()) == fieldName){
            return true;
        }
    }
    return false;
}*/

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
    if (value.isObject()){
        QJsonObject json_object = value.toObject();
        for (int i=0; i<json_object.keys().count(); i++){
            QString fieldName = json_object.keys().at(i);
            setFieldValue(fieldName, json_object[fieldName].toVariant());
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
    }*//*
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
    }*/
    //qDebug() << object;

    for (int i=0; i<m_fieldsValue.count(); i++){
        QString fieldName = m_fieldsValue.keys().at(i);
        // Ignore "metaObject" properties
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

    return object;
}
