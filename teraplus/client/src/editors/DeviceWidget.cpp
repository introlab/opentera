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

    // Query available sites
    QUrlQuery args;
    args.addQueryItem(WEB_QUERY_LIST, "");
    queryDataRequest(WEB_SITEINFO_PATH, args);

    // Query associated participants and session types
    if (!dataIsNew()){
        args.removeAllQueryItems(WEB_QUERY_LIST);
        args.addQueryItem(WEB_QUERY_ID_DEVICE, QString::number(m_data->getId()));
        queryDataRequest(WEB_DEVICEPARTICIPANTINFO_PATH, args);

        args.removeAllQueryItems(WEB_QUERY_ID_DEVICE);
        args.addQueryItem(WEB_QUERY_ID_DEVICE_TYPE, m_data->getFieldValue("device_type").toString());
        queryDataRequest(WEB_SESSIONTYPEDEVICETYPE_PATH, args);
    }
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
   ui->tabSites->setEnabled(!dataIsNew());
}

void DeviceWidget::updateFieldsValue()
{
    if (m_data && !hasPendingDataRequests()){
        if (!ui->wdgDevice->formHasData()){
            ui->wdgDevice->fillFormFromData(m_data->toJson());
        }else {
            ui->wdgDevice->resetFormValues();
        }
    }
}

bool DeviceWidget::validateData()
{
    return ui->wdgDevice->validateFormData();
}

void DeviceWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &DeviceWidget::processFormsReply);
    connect(m_comManager, &ComManager::sitesReceived, this, &DeviceWidget::processSitesReply);
    connect(m_comManager, &ComManager::deviceSitesReceived, this, &DeviceWidget::processDeviceSitesReply);
    connect(m_comManager, &ComManager::deviceParticipantsReceived, this, &DeviceWidget::processDeviceParticipantsReply);
    connect(m_comManager, &ComManager::sessionTypesDeviceTypesReceived, this, &DeviceWidget::processSessionTypesReply);

    connect(ui->btnSave, &QPushButton::clicked, this, &DeviceWidget::btnSave_clicked);
    connect(ui->btnUndo, &QPushButton::clicked, this, &DeviceWidget::btnUndo_clicked);
    connect(ui->btnSites, &QPushButton::clicked, this, &DeviceWidget::btnSaveSites_clicked);
}

void DeviceWidget::updateSite(TeraData *site)
{
    int id_site = site->getId();
    if (m_listSites_items.contains(id_site)){
        QListWidgetItem* item = m_listSites_items[id_site];
        item->setText(site->getName());
    }else{
        QListWidgetItem* item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_SITE)), site->getName());
        item->setCheckState(Qt::Unchecked);
        ui->lstSites->addItem(item);
        m_listSites_items[id_site] = item;
    }
}

void DeviceWidget::updateParticipant(TeraData *participant)
{
    int id_participant = participant->getFieldValue("id_participant").toInt();
    QString participant_name = participant->getFieldValue("participant_name").toString();
    if (m_listParticipants_items.contains(id_participant)){
        QListWidgetItem* item = m_listParticipants_items[id_participant];
        item->setText(participant_name);
    }else{
        QListWidgetItem* item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_PARTICIPANT)), participant_name);
        ui->lstParticipants->addItem(item);
        m_listParticipants_items[id_participant] = item;
    }
}

void DeviceWidget::updateSessionType(TeraData *session_type)
{
    int id_session_type = session_type->getFieldValue("id_session_type").toInt();
    QString session_type_name = session_type->getFieldValue("session_type_name").toString();
    if (m_listSessionTypes_items.contains(id_session_type)){
        QListWidgetItem* item = m_listSessionTypes_items[id_session_type];
        item->setText(session_type_name);
    }else{
        QListWidgetItem* item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_SESSIONTYPE)), session_type_name);
        ui->lstSessionTypes->addItem(item);
        m_listSessionTypes_items[id_session_type] = item;
    }
}

void DeviceWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_DEVICE){
        ui->wdgDevice->buildUiFromStructure(data);
        return;
    }

}

void DeviceWidget::processSitesReply(QList<TeraData> sites)
{
    // If our site list is empty, already query sites for that device
    bool need_to_load_device_sites = m_listSites_items.isEmpty();

    for(TeraData site:sites){
        updateSite(&site);
    }

    if (need_to_load_device_sites && !dataIsNew()){
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_ID_DEVICE, QString::number(m_data->getId()));
        args.addQueryItem(WEB_QUERY_LIST, "");
        queryDataRequest(WEB_DEVICESITEINFO_PATH, args);
    }
}

void DeviceWidget::processDeviceSitesReply(QList<TeraData> device_sites)
{
    if (device_sites.isEmpty())
        return;

    // Check if it is for us
    if (device_sites.first().getFieldValue("id_device").toInt() != m_data->getId())
        return;

    // Uncheck all sites
    for (QListWidgetItem* item:m_listSites_items){
        item->setCheckState(Qt::Unchecked);
    }
    m_listDeviceSites_items.clear();

    // Check required sites
    for(TeraData device_site:device_sites){
        int site_id = device_site.getFieldValue("id_site").toInt();
        int device_site_id = device_site.getId();
        if (m_listSites_items.contains(site_id)){
            m_listSites_items[site_id]->setCheckState(Qt::Checked);
            m_listDeviceSites_items[device_site_id] = m_listSites_items[site_id];
        }
    }
}

void DeviceWidget::processDeviceParticipantsReply(QList<TeraData> device_parts)
{
    if (device_parts.isEmpty())
        return;

    // Check if it is for us
    if (device_parts.first().getFieldValue("id_device").toInt() != m_data->getId())
        return;

    for (TeraData device_part:device_parts){
        updateParticipant(&device_part);
    }
}

void DeviceWidget::processSessionTypesReply(QList<TeraData> session_types)
{
    if (session_types.isEmpty())
        return;

    // Check if it is for us
    if (session_types.first().getFieldValue("id_device_type").toInt() != m_data->getFieldValue("device_type").toInt())
        return;

    for (TeraData session_type:session_types){
        updateSessionType(&session_type);
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

void DeviceWidget::btnSaveSites_clicked()
{
    QJsonDocument document;
    QJsonObject base_obj;
    QJsonArray devices;
    QList<int> sites_to_delete;

    for (int i=0; i<ui->lstSites->count(); i++){
        // Build json list of devices and sites
        if (ui->lstSites->item(i)->checkState()==Qt::Checked){
            QJsonObject item_obj;
            item_obj.insert("id_device", m_data->getId());
            item_obj.insert("id_site", m_listSites_items.key(ui->lstSites->item(i)));
            devices.append(item_obj);
        }else{
            int id_device_site = m_listDeviceSites_items.key(ui->lstSites->item(i),-1);
            if (id_device_site>=0){
                sites_to_delete.append(id_device_site);
            }
        }
    }

    // Delete queries
    for (int id_device_site:sites_to_delete){
        deleteDataRequest(WEB_DEVICESITEINFO_PATH, id_device_site);
    }

    if (!sites_to_delete.isEmpty()){
        // Also refresh participants
        ui->lstParticipants->clear();
        m_listParticipants_items.clear();
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_ID_DEVICE, QString::number(m_data->getId()));
        queryDataRequest(WEB_DEVICEPARTICIPANTINFO_PATH, args);
    }

    // Update query
    base_obj.insert("device_site", devices);
    document.setObject(base_obj);
    postDataRequest(WEB_DEVICESITEINFO_PATH, document.toJson());

}
