#ifndef TERADATA_H
#define TERADATA_H

#include <QObject>
#include <QJsonValue>
#include <QJsonArray>
#include <QJsonObject>

#include <QMetaProperty>

#include "webapi.h"

enum TeraDataTypes {
    TERADATA_NONE,
    TERADATA_USER,
    TERADATA_SITE,
    TERADATA_KIT,
    TERADATA_SESSIONTYPE,
    TERADATA_TESTDEF,
    TERADATA_PROJECT,
    TERADATA_DEVICE,
    TERADATA_GROUP,
    TERADATA_PARTICIPANT,
    TERADATA_SITEACCESS,
    TERADATA_PROJECTACCESS,
    TERADATA_KITDEVICE
};

Q_DECLARE_METATYPE(TeraDataTypes)

class TeraData : public QObject
{
    Q_OBJECT

    Q_PROPERTY(int id READ getId)
    Q_PROPERTY(QString name READ getName)
    Q_PROPERTY(TeraDataTypes data_type READ getDataType WRITE setDataType)

public:
    //explicit TeraData(QObject *parent = nullptr);
    explicit TeraData(TeraDataTypes obj_type, QObject *parent = nullptr);
    TeraData(const TeraData& copy, QObject *parent=nullptr);
    explicit TeraData(TeraDataTypes obj_type, const QJsonValue& json, QObject *parent = nullptr);

    virtual bool        fromJson(const QJsonValue& value);
    virtual QJsonObject toJson();

    int getId() const;
    QString getIdFieldName() const;
    void setId(const int& id);
    virtual QString getName() const;
    void setName(const QString& name);

    bool isNew();

    virtual TeraData &operator = (const TeraData& other);
    virtual bool operator == (const TeraData& other) const;

    TeraDataTypes getDataType() const;
    bool hasFieldName(const QString& fieldName) const;
    void removeFieldName(const QString& fieldName);
    QVariant getFieldValue(const QString &fieldName) const;
    void setFieldValue(const QString& fieldName, const QVariant& fieldValue);
    QList<QString> getFieldList() const;

    static QString getDataTypeName(const TeraDataTypes& data_type);
    static TeraDataTypes getDataTypeFromPath(const QString& path);
    static QString getPathForDataType(const TeraDataTypes& data_type);

    static QString getIconFilenameForDataType(const TeraDataTypes& data_type);

protected:

    TeraDataTypes   m_data_type;

private:
    QString     m_objectName;
    QString     m_idField;
    QString     m_nameField;

    QVariantMap m_fieldsValue;

    //bool hasMetaProperty(const QString& fieldName) const;

signals:


public slots:
    void setDataType(TeraDataTypes data_type);

};

#endif // TERADATA_H
