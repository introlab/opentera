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

private:
    Ui::TeraForm*                                   ui;
    QMap<QString, QWidget*>                         m_widgets;
    QMap<QWidget*, QFormLayout::TakeRowResult>      m_hidden_rows;

    void buildFormFromStructure(QWidget* page, const QVariantList &structure);
    void setDefaultValues();

    QWidget* createVideoInputsWidget(const QVariantMap& structure);
    QWidget* createAudioInputsWidget(const QVariantMap& structure);
    QWidget* createArrayWidget(const QVariantMap& structure);
    QWidget* createTextWidget(const QVariantMap& structure, bool is_masked);
    QWidget* createBooleanWidget(const QVariantMap& structure);
    QWidget* createNumericWidget(const QVariantMap& structure);

    void checkConditions();
    void setWidgetVisibility(QWidget* widget, bool visible);
    void getWidgetValues(QWidget *widget, QVariant *id, QVariant* value);

private slots:
    void widgetValueChanged();

};

#endif // TERAFORM_H
