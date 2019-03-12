#ifndef TERADATA_H
#define TERADATA_H

#include <QObject>
#include <QJsonValue>
#include <QJsonArray>
#include <QJsonObject>

#include <QMetaProperty>

class TeraData : public QObject
{
    Q_OBJECT

    Q_PROPERTY(int id READ getId WRITE setId NOTIFY idChanged)
    Q_PROPERTY(QString name READ getName WRITE setName NOTIFY nameChanged)
    Q_PROPERTY(QString class_name READ getClassName)

public:
    explicit TeraData(QObject *parent = nullptr);
    explicit TeraData(const TeraData& copy, QObject *parent=nullptr);
    explicit TeraData(const QJsonValue& json, QObject *parent = nullptr);

    virtual bool        fromJson(const QJsonValue& value);
    virtual QJsonObject toJson();

    int getId() const;
    virtual QString getName() const;

    virtual TeraData &operator = (const TeraData& other);
    virtual bool operator == (const TeraData& other) const;

    QString getClassName() const;

protected:
    int         m_id;
    QString     m_name;
signals:

    void idChanged();
    void nameChanged(QString name);

public slots:
    void setId(int id);
    void setName(QString name);
};

#endif // TERADATA_H
