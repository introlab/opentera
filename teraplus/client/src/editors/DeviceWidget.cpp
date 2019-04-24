#include "DeviceWidget.h"
#include "GlobalMessageBox.h"

#include "ui_DeviceWidget.h"

DeviceWidget::DeviceWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::DeviceWidget)
{
    if (parent){
        ui->setupUi(parent);
    }else {
        ui->setupUi(this);
    }
    setAttribute(Qt::WA_StyledBackground); //Required to set a background image

    // Connect signals and slots
    connectSignals();

    // Query forms definition
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_DEVICE));
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_KIT_DEVICE));

}

DeviceWidget::~DeviceWidget()
{
    delete ui;
}

void DeviceWidget::saveData(bool signal)
{
    // Site data
    QJsonDocument device_data = ui->wdgDevice->getFormDataJson(m_data->isNew());

    //qDebug() << user_data.toJson();
    postDataRequest(WEB_DEVICEINFO_PATH, device_data.toJson());

    if (signal){
        TeraData* new_data = ui->wdgDevice->getFormDataObject(TERADATA_DEVICE);
        *m_data = *new_data;
        delete new_data;
        emit dataWasChanged();
    }
}

void DeviceWidget::updateControlsState()
{

}

void DeviceWidget::updateFieldsValue()
{
    if (m_data && !hasPendingDataRequests()){
        if (!ui->wdgDevice->formHasData())
            ui->wdgDevice->fillFormFromData(m_data->toJson());
        else {
            ui->wdgDevice->resetFormValues();
        }
    }
}

bool DeviceWidget::validateData()
{

    return true;
}

void DeviceWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &DeviceWidget::processFormsReply);

    connect(ui->btnSave, &QPushButton::clicked, this, &DeviceWidget::btnSave_clicked);
    connect(ui->btnUndo, &QPushButton::clicked, this, &DeviceWidget::btnUndo_clicked);
}

void DeviceWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_DEVICE){
        ui->wdgDevice->buildUiFromStructure(data);
        return;
    }
    if (form_type == WEB_FORMS_QUERY_KIT_DEVICE){
        ui->wdgKitDevice->buildUiFromStructure(data);
        return;
    }
}

void DeviceWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgDevice->getInvalidFormDataLabels();

        QString msg = tr("Les champs suivants doivent être complétés:") +" <ul>";
        for (QString field:invalids){
            msg += "<li>" + field + "</li>";
        }
        msg += "</ul>";
        GlobalMessageBox msgbox(this);
        msgbox.showError(tr("Champs invalides"), msg);
        return;
    }

     saveData();
}

void DeviceWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();
}
