#include "KitWidget.h"
#include "ui_KitWidget.h"

#include "GlobalMessageBox.h"

#include <QDebug>

KitWidget::KitWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::KitWidget)
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
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_KIT));

    // Query project list (to ensure sites and projects sync)
    queryDataRequest(WEB_PROJECTINFO_PATH, QUrlQuery());

    // Query available devices
    QUrlQuery query;
    query.addQueryItem(WEB_QUERY_LIST,"");
    query.addQueryItem(WEB_QUERY_AVAILABLE, "");
    queryDataRequest(WEB_DEVICEINFO_PATH, query);

}

KitWidget::~KitWidget()
{
    delete ui;
}

void KitWidget::saveData(bool signal)
{
    //Get data
    QJsonDocument kit_data = ui->wdgKit->getFormDataJson(m_data->isNew());

    postDataRequest(WEB_KITINFO_PATH, kit_data.toJson());

    if (signal){
        TeraData* new_data = ui->wdgKit->getFormDataObject(TERADATA_KIT);
        *m_data = *new_data;
        delete new_data;
        emit dataWasChanged();
    }
}

void KitWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &KitWidget::processFormsReply);
    connect(m_comManager, &ComManager::projectsReceived, this, &KitWidget::processProjectsReply);
    connect(m_comManager, &ComManager::devicesReceived, this, &KitWidget::processDevicesReply);

    connect(ui->wdgKit, &TeraForm::widgetValueHasChanged, this, &KitWidget::wdgKitWidgetValueChanged);
    connect(ui->btnSave, &QPushButton::clicked, this, &KitWidget::btnSave_clicked);
    connect(ui->btnUndo, &QPushButton::clicked, this, &KitWidget::btnUndo_clicked);
}

void KitWidget::updateDevice(const TeraData *device)
{
    int id_device = device->getId();
    if (m_listDevices_items.contains(id_device)){
        QListWidgetItem* item = m_listDevices_items[id_device];
        item->setText(device->getName());
    }else{
        QListWidgetItem* item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)), device->getName());
        ui->lstDevices->addItem(item);
        m_listDevices_items[id_device] = item;
    }
}

void KitWidget::updateControlsState()
{

}

void KitWidget::updateFieldsValue()
{
    if (m_data && !hasPendingDataRequests()){
        if (!ui->wdgKit->formHasData())
            ui->wdgKit->fillFormFromData(m_data->toJson());
        else {
            ui->wdgKit->resetFormValues();
        }
    }
}

bool KitWidget::validateData()
{
    return ui->wdgKit->validateFormData();
}

void KitWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_KIT){
        ui->wdgKit->buildUiFromStructure(data);
        return;
    }
}

void KitWidget::processProjectsReply(QList<TeraData> projects)
{
    if (m_projects.isEmpty())
        m_projects = projects;

}

void KitWidget::processDevicesReply(QList<TeraData> devices)
{
    qDebug() << "processDevicesReply";
    for (int i=0; i<devices.count(); i++){
        updateDevice(&devices.at(i));
    }
}

void KitWidget::wdgKitWidgetValueChanged(QWidget *widget, QVariant value)
{
    // We consider only the site field to adjust project list
    if (widget == ui->wdgKit->getWidgetForField("id_site")){
        QComboBox* combo_project = dynamic_cast<QComboBox*>(ui->wdgKit->getWidgetForField("id_project"));
        int site_id = value.toInt();
        if (combo_project){
            int current_data = combo_project->currentData().toInt();
            combo_project->clear();
            // Add empty item
            combo_project->addItem("", "");
            for (int i=0; i<m_projects.count(); i++){
                if (m_projects.at(i).getFieldValue("id_site").toInt() == site_id){
                    combo_project->addItem(m_projects.at(i).getName(), m_projects.at(i).getId());
                }
            }
            int current_index = combo_project->findData(current_data);
            if (current_index>=0){
                combo_project->setCurrentIndex(current_index);
            }else{
                combo_project->setCurrentIndex(0); // Empty item
            }
        }else{
            LOG_ERROR("Unable to find project list combo!", "KitWidget::wdgKitWidgetValueChanged");
        }
    }
}

void KitWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgKit->getInvalidFormDataLabels();

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

void KitWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();
}
