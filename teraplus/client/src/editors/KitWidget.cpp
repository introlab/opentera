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
    ui->btnAddDevice->setEnabled(false);
    ui->btnDelDevice->setEnabled(false);

    // Connect signals and slots
    connectSignals();

    // Query forms definition
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_KIT));

    // Query project list (to ensure sites and projects sync)
    queryDataRequest(WEB_PROJECTINFO_PATH, QUrlQuery());

    QUrlQuery query;
    // Query available devices
    query.addQueryItem(WEB_QUERY_LIST,"");
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
    connect(m_comManager, &ComManager::kitDevicesReceived, this, &KitWidget::processKitDevicesReply);
    connect(m_comManager, &ComManager::deleteResultsOK, this, &KitWidget::processDeleteDataReply);

    connect(ui->wdgKit, &TeraForm::widgetValueHasChanged, this, &KitWidget::wdgKitWidgetValueChanged);
    connect(ui->btnSave, &QPushButton::clicked, this, &KitWidget::btnSave_clicked);
    connect(ui->btnUndo, &QPushButton::clicked, this, &KitWidget::btnUndo_clicked);
    connect(ui->lstDevices, &QListWidget::currentItemChanged, this, &KitWidget::lstDeviceCurrentChanged);
    connect(ui->lstKitDevices, &QListWidget::currentItemChanged, this, &KitWidget::lstKitDeviceCurrentChanged);
    connect(ui->btnAddDevice, &QPushButton::clicked, this, &KitWidget::btnAddDevice_clicked);
    connect(ui->btnDelDevice, &QPushButton::clicked, this, &KitWidget::btnDelDevice_clicked);
}

void KitWidget::updateDevice(const TeraData *device)
{
    int id_device = device->getId();
    QListWidgetItem* item;
    if (m_listDevices_items.contains(id_device)){
        item = m_listDevices_items[id_device];
        item->setText(device->getName());
    }else{
        item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)), device->getName());
        ui->lstDevices->addItem(item);
        m_listDevices_items[id_device] = item;
        m_ids_devices[id_device] = TeraData(*device);
    }

    // Update visual according to status
    item->setTextColor(QColor(Qt::white));
    item->setIcon(QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)));
    bool wrong_list = false;
    if (device->hasFieldName("id_kit")){
        // Device is already assigned to a kit.
        if (device->getFieldValue("id_kit").toInt()==m_data->getId()){
            // Device is for that kit - ensure it is in the correct list
            if (device->hasFieldName("kit_device_optional")){
                if (!device->getFieldValue("kit_device_optional").toBool())
                    item->setIcon(QIcon(":/icons/device_online.png"));
            }
            wrong_list = true;
        }else{
            item->setTextColor(QColor(Qt::darkRed));
            item->setIcon(QIcon(":/icons/device_installed.png"));
            item->setText(item->text() + " [" + device->getFieldValue("kit_name").toString() + "]");
        }
    }else{
        if (item->listWidget() == ui->lstKitDevices){
            // Wrong list for that item - switch it!
            wrong_list = true;
        }
    }

    // Check if we need to switch the item from lists
    if (wrong_list){
        QListWidget* item_src = item->listWidget();
        QListWidget* item_dst;
        if (item_src == ui->lstDevices){
            item_dst = ui->lstKitDevices;
        }else{
            item_dst = ui->lstDevices;
        }
        int item_row = item_src->row(item);
        item_src->takeItem(item_row);
        item_row = item_dst->row(item);
        item_dst->addItem(item);
    }
}

void KitWidget::updateControlsState()
{
    ui->tabDevices->setEnabled(!dataIsNew());
    ui->tabParticipants->setEnabled(!dataIsNew());
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
    bool first_list = ui->lstDevices->count()==0;
    for (int i=0; i<devices.count(); i++){
        updateDevice(&devices.at(i));
    }
    if (first_list){
        // Query unavailable devices
        QUrlQuery query;
        query.addQueryItem(WEB_QUERY_ID_KIT, QString::number(m_data->getId()));
        queryDataRequest(WEB_KITDEVICE_PATH, query);
    }
}

void KitWidget::processKitDevicesReply(QList<TeraData> kit_devices)
{

    for (int i=0; i<kit_devices.count(); i++){
        // Get device
        int id_device = kit_devices.at(i).getFieldValue("id_device").toInt();
        TeraData* device = &m_ids_devices[id_device];

        if (device){
            // Found it - update values
            device->setFieldValue("id_kit", kit_devices.at(i).getFieldValue("id_kit"));
            device->setFieldValue("kit_device_optional", kit_devices.at(i).getFieldValue("kit_device_optional"));
            device->setFieldValue("id_kit_device", kit_devices.at(i).getId());
        }
        updateDevice(device);
    }

}

void KitWidget::processDeleteDataReply(QString path, int id)
{
    if (path == WEB_KITDEVICE_PATH){
        // Kit-Device was deleted
        for (int i=0; i<m_ids_devices.count(); i++){
            TeraData* device = &m_ids_devices[m_ids_devices.keys().at(i)];
            if (device->hasFieldName("id_kit_device")){
                if (device->getFieldValue("id_kit_device").toInt()==id){
                    // We must update...
                    device->removeFieldName("id_kit");
                    device->removeFieldName("kit_device_optional");
                    device->removeFieldName("id_kit_device");
                    updateDevice(device);
                    break;
                }
            }
        }
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

void KitWidget::lstDeviceCurrentChanged(QListWidgetItem *current, QListWidgetItem *previous)
{
    Q_UNUSED(previous)
    bool available = false;
    if (current){
        int id = m_listDevices_items.key(current, -1);
        if (id>=0){
            if (m_ids_devices.contains(id)){
                if (!m_ids_devices.value(id).hasFieldName("id_kit") ||
                        (m_ids_devices.value(id).hasFieldName("id_kit") &&
                         m_ids_devices.value(id).getFieldValue("id_kit").toInt()==m_data->getId()))
                    available = true;
            }

        }

    }
    ui->btnAddDevice->setEnabled(current && available);
}

void KitWidget::lstKitDeviceCurrentChanged(QListWidgetItem *current, QListWidgetItem *previous)
{
    Q_UNUSED(previous)
    ui->btnDelDevice->setEnabled(current);
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

void KitWidget::btnAddDevice_clicked()
{
    for (QListWidgetItem* item:ui->lstDevices->selectedItems()){
        int item_id = m_listDevices_items.key(item);
        TeraData* item_data = &m_ids_devices[item_id];

        if (item_data){

            item_data->setFieldValue("kit_device_optional", ui->chkOptional->isChecked());
            item_data->setFieldValue("id_kit", m_data->getId());
            QJsonDocument document;
            QJsonObject base_obj;
            QJsonArray devices;

           // Build json list of devices for that kit
            base_obj.insert("id_kit", m_data->getId());
            base_obj.insert("id_device", item_id);
            base_obj.insert("kit_device_optional", item_data->getFieldValue("kit_device_optional").toBool());
            devices.append(base_obj);

           // Post that list!
            if (!devices.isEmpty()){
                base_obj.insert("kit_device", devices);
                document.setObject(base_obj);
                postDataRequest(WEB_KITDEVICE_PATH, document.toJson());
            }
            //updateDevice(item_data);
        }
    }
}

void KitWidget::btnDelDevice_clicked()
{
    for (QListWidgetItem* item:ui->lstKitDevices->selectedItems()){
        int item_id = m_listDevices_items.key(item);
        TeraData* item_data = &m_ids_devices[item_id];

        if (item_data){
            int kit_device_id = item_data->getFieldValue("id_kit_device").toInt();
            //item->setIcon(QIcon(":/icons/device.png"));
            //updateDevice(item_data);
            deleteDataRequest(WEB_KITDEVICE_PATH, kit_device_id);
        }

        //ui->lstKitDevices->takeItem(ui->lstKitDevices->row(item));
        //ui->lstDevices->addItem(item);
    }
}

