#ifndef TERADATA_H
#define TERADATA_H

#include <QObject>
#include <QJsonValue>
#include <QJsonArray>
#include <QJsonObject>

#include <QMetaProperty>

enum TeraDataTypes {
    TERADATA_USER,
    TERADATA_SITE,
    TERADATA_KIT,
    TERADATA_SESSIONTYPE,
    TERADATA_TESTDEF
};

Q_DECLARE_METATYPE(TeraDataTypes)

class TeraData : public QObject
{
    Q_OBJECT

    Q_PROPERTY(int id READ getId)
    Q_PROPERTY(QString name READ getName)
    Q_PROPERTY(TeraDataTypes data_type READ getDataType WRITE setDataType)

public:
    explicit TeraData(TeraDataTypes obj_type, QObject *parent = nullptr);
    explicit TeraData(const TeraData& copy, QObject *parent=nullptr);
    explicit TeraData(TeraDataTypes obj_type, const QJsonValue& json, QObject *parent = nullptr);

    virtual bool        fromJson(const QJsonValue& value);
    virtual QJsonObject toJson();

    int getId() const;
    virtual QString getName() const;

    virtual TeraData &operator = (const TeraData& other);
    virtual bool operator == (const TeraData& other) const;

    TeraDataTypes getDataType() const;
    bool hasFieldName(const QString& fieldName) const;
    QVariant getFieldValue(const QString &fieldName) const;
    void setFieldValue(const QString& fieldName, const QVariant& fieldValue);
    QList<QString> getFieldList() const;

    static QString getDataTypeName(const TeraDataTypes data_type);

protected:

    TeraDataTypes   m_data_type;

private:
    QString m_objectName;
    QString m_idField;
    QString m_nameField;

    bool hasMetaProperty(const QString& fieldName) const;

signals:


public slots:
    void setDataType(TeraDataTypes data_type);

};

#endif // TERADATA_H
