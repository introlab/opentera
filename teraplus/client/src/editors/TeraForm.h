#ifndef TERAFORM_H
#define TERAFORM_H

#include <QJsonDocument>
#include <QJsonParseError>
#include <QJsonArray>
#include <QJsonObject>

#include <QVariantList>
#include <QVariantMap>

#include <QWidget>
#include <QLabel>
#include <QComboBox>
#include <QFormLayout>
#include <QLineEdit>
#include <QCheckBox>
#include <QSpinBox>
#include <QFrame>
#include <QListWidget>
#include <QTextEdit>

#include <QtMultimedia/QCameraInfo>
#include <QtMultimedia/QAudioDeviceInfo>

namespace Ui {
class TeraForm;
}

class TeraForm : public QWidget
{
    Q_OBJECT

public:
    explicit TeraForm(QWidget *parent = nullptr);
    ~TeraForm();

    void buildUiFromStructure(const QString& structure);
    void fillFormFromData(const QJsonObject& data);
    void fillFormFromData(const QString& structure);
    bool formHasData();
    void resetFormValues();

    bool validateFormData(bool include_hidden=false);
    QStringList getInvalidFormDataLabels(bool include_hidden=false);

    QWidget* getWidgetForField(const QString& field);
    bool setFieldValue(const QString& field, const QVariant& value);
    QVariant getFieldValue(const QString& field);

    QString getFormData(bool include_unmodified_data=false);
    QJsonDocument getFormDataJson(bool include_unmodified_data=false);

private:
    Ui::TeraForm*                                   ui;
    QMap<QString, QWidget*>                         m_widgets;
    QMap<QWidget*, QFormLayout::TakeRowResult>      m_hidden_rows;
    QString                                         m_objectType;
    QVariantMap                                     m_initialValues;

    void buildFormFromStructure(QWidget* page, const QVariantList &structure);
    void setDefaultValues();

    QWidget* createVideoInputsWidget(const QVariantMap& structure);
    QWidget* createAudioInputsWidget(const QVariantMap& structure);
    QWidget* createArrayWidget(const QVariantMap& structure);
    QWidget* createTextWidget(const QVariantMap& structure, bool is_masked);
    QWidget* createBooleanWidget(const QVariantMap& structure);
    QWidget* createNumericWidget(const QVariantMap& structure);
    QWidget* createLabelWidget(const QVariantMap& structure);
    QWidget* createListWidget(const QVariantMap& structure);
    QWidget* createLongTextWidget(const QVariantMap& structure);

    void checkConditions();
    void checkConditionsForItem(QWidget* item);
    void setWidgetVisibility(QWidget* widget, QWidget *linked_widget, bool visible);
    void getWidgetValues(QWidget *widget, QVariant *id, QVariant* value);
    void setWidgetValue(QWidget* widget, const QVariant& value);

    bool validateWidget(QWidget* widget, bool include_hidden=false);

private slots:
    void widgetValueChanged();

};

#endif // TERAFORM_H
