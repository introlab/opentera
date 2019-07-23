#include "SiteWidget.h"
#include "ui_SiteWidget.h"

#include "editors/DataListWidget.h"

SiteWidget::SiteWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::SiteWidget)
{
    m_diag_editor = nullptr;

    if (parent){
        ui->setupUi(parent);
    }else {
        ui->setupUi(this);
    }
    setAttribute(Qt::WA_StyledBackground); //Required to set a background image

    // Limited by default
    m_limited = true;

    // Connect signals and slots
    connectSignals();

    // Query forms definition
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_SITE));

    // Query accessible users list
    queryDataRequest(WEB_USERINFO_PATH, QUrlQuery(WEB_QUERY_LIST));

    setData(data);
}

SiteWidget::~SiteWidget()
{
    delete ui;

}

void SiteWidget::saveData(bool signal)
{
    // Site data
    QJsonDocument site_data = ui->wdgSite->getFormDataJson(m_data->isNew());

    //qDebug() << user_data.toJson();
    postDataRequest(WEB_SITEINFO_PATH, site_data.toJson());

    if (signal){
        TeraData* new_data = ui->wdgSite->getFormDataObject(TERADATA_SITE);
        *m_data = *new_data;
        delete new_data;
        emit dataWasChanged();
    }
}

void SiteWidget::setData(const TeraData *data)
{
    DataEditorWidget::setData(data);

    // Query projects & devices
    if (!dataIsNew()){
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_ID_SITE, QString::number(data->getFieldValue("id_site").toInt()));
        args.addQueryItem(WEB_QUERY_LIST, "");
        queryDataRequest(WEB_PROJECTINFO_PATH, args);

        // Query full devices information
        args.removeQueryItem(WEB_QUERY_LIST);
        args.addQueryItem(WEB_QUERY_PARTICIPANTS, "");
        args.addQueryItem(WEB_QUERY_SITES, "");
        queryDataRequest(WEB_DEVICEINFO_PATH, args);
    }else{
        ui->tabSiteInfos->setEnabled(false);
    }
}

void SiteWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &SiteWidget::processFormsReply);
    connect(m_comManager, &ComManager::siteAccessReceived, this, &SiteWidget::processSiteAccessReply);
    connect(m_comManager, &ComManager::usersReceived, this, &SiteWidget::processUsersReply);
    connect(m_comManager, &ComManager::projectsReceived, this, &SiteWidget::processProjectsReply);
    connect(m_comManager, &ComManager::devicesReceived, this, &SiteWidget::processDevicesReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &SiteWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &SiteWidget::btnSave_clicked);
    connect(ui->btnUpdateRoles, &QPushButton::clicked, this, &SiteWidget::btnUpdateAccess_clicked);
    //connect(ui->btnProjects, &QPushButton::clicked, this, &SiteWidget::btnProjects_clicked);
    connect(ui->btnDevices, &QPushButton::clicked, this, &SiteWidget::btnDevices_clicked);
    connect(ui->btnUsers, &QPushButton::clicked, this, &SiteWidget::btnUsers_clicked);

}

void SiteWidget::updateSiteAccess(const TeraData *access)
{
    if (m_tableUsers_ids_rows.contains(access->getFieldValue("id_user").toInt())){
        // Already there - update the user access
        int row = m_tableUsers_ids_rows[access->getFieldValue("id_user").toInt()];
        QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableUsers->cellWidget(row,1));
        if (combo_roles){
            int index = -1;
            if (access->hasFieldName("site_access_role"))
                index = combo_roles->findData(access->getFieldValue("site_access_role").toString());
            if (index >= 0){
                combo_roles->setCurrentIndex(index);
            }else{
                combo_roles->setCurrentIndex(0);
            }
            combo_roles->setProperty("original_index", index);

            if (access->hasFieldName("site_access_inherited")){
                if (access->getFieldValue("site_access_inherited").toBool()){
                    // Inherited access - disable combobox
                    combo_roles->setDisabled(true);
                }
            }
        }
    }else{
        // Not there - must add the user
        ui->tableUsers->setRowCount(ui->tableUsers->rowCount()+1);
        int current_row = ui->tableUsers->rowCount()-1;
        QTableWidgetItem* item = new QTableWidgetItem(access->getFieldValue("user_name").toString());
        ui->tableUsers->setItem(current_row,0,item);
        QComboBox* combo_roles = buildRolesComboBox();
        ui->tableUsers->setCellWidget(current_row,1,combo_roles);
        m_tableUsers_ids_rows.insert(access->getFieldValue("id_user").toInt(), current_row);
    }
}

void SiteWidget::updateProject(const TeraData *project)
{
    int id_project = project->getId();
    if (m_listProjects_items.contains(id_project)){
        QListWidgetItem* item = m_listProjects_items[id_project];
        item->setText(project->getName());
    }else{
        QListWidgetItem* item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_PROJECT)), project->getName());
        ui->lstProjects->addItem(item);
        m_listProjects_items[id_project] = item;
    }
}

void SiteWidget::updateDevice(const TeraData *device)
{
    int id_device = device->getId();

    // Create list of projects and participants
    QStringList projects;
    QStringList participants;
    if (device->hasFieldName("device_participants")){
        QVariantList part_list = device->getFieldValue("device_participants").toList();
        for (QVariant part:part_list){
            QVariantMap part_info = part.toMap();
            QString project_name = tr("Project inconnu");
            QString participant_name = "";
            if (part_info.contains("participant_name")){
                participant_name = part_info["participant_name"].toString();
            }
            if (part_info.contains("project_name")){
                project_name = part_info["project_name"].toString();
            }
            projects.append(project_name);
            participants.append(participant_name);
        }
    }

    // Build assignment string
    QString assignment="";
    for (int i=0; i<participants.count(); i++){
        if (i>0)
            assignment += ", ";
        assignment += participants.at(i);
        if (!participants.at(i).isEmpty())
            assignment += " (" + projects.at(i) + ")";
    }

    // Build device name, if empty
    QString device_name = device->getName();
    if (device_name.isEmpty())
        device_name = tr("(Appareil sans nom)");

    // Create / update values in table
    if (m_listDevices_items.contains(id_device)){
       QTableWidgetItem* item = m_listDevices_items[id_device];
       item->setText(device_name);
       ui->lstDevices->item(item->row(), 1)->setText(assignment);
    }else{
        ui->lstDevices->setRowCount(ui->lstDevices->rowCount()+1);
        QTableWidgetItem* item = new QTableWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)), device->getName());
        ui->lstDevices->setItem(ui->lstDevices->rowCount()-1, 0, item);
        m_listDevices_items[id_device] = item;

        item = new QTableWidgetItem(assignment);
        ui->lstDevices->setItem(ui->lstDevices->rowCount()-1, 1, item);
    }  

}

void SiteWidget::updateControlsState()
{
    ui->btnDevices->setVisible(!m_limited);
    ui->btnUsers->setVisible(!m_limited);
    //ui->btnProjects->setVisible(!m_limited);

}

void SiteWidget::updateFieldsValue()
{
    if (m_data){
        ui->wdgSite->fillFormFromData(m_data->toJson());
    }
}

bool SiteWidget::validateData()
{
    return ui->wdgSite->validateFormData();
}

void SiteWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_SITE){
        ui->wdgSite->buildUiFromStructure(data);
        return;
    }
}

void SiteWidget::processSiteAccessReply(QList<TeraData> access)
{
    if (!m_data)
        return;

    for (int i=0; i<access.count(); i++){
        if (access.at(i).getFieldValue("id_site").toInt() == m_data->getFieldValue("id_site").toInt()){
            // Ok, we need to update information in the table
            updateSiteAccess(&access.at(i));
        }

    }
}

void SiteWidget::processUsersReply(QList<TeraData> users)
{
    for (int i=0; i<users.count(); i++){
        updateSiteAccess(&users.at(i));
    }

    // Query access for those users
    if (m_data && !dataIsNew()){
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_ID_SITE, QString::number(m_data->getFieldValue("id_site").toInt()));
        queryDataRequest(WEB_SITEACCESS_PATH, args);
    }
}

void SiteWidget::processProjectsReply(QList<TeraData> projects)
{
    if (!m_data)
        return;

    for (int i=0; i<projects.count(); i++){
        if (projects.at(i).getFieldValue("id_site") == m_data->getFieldValue("id_site")){
            updateProject(&projects.at(i));
        }
    }
}

void SiteWidget::processDevicesReply(QList<TeraData> devices)
{
    if (!m_data)
        return;

    for (int i=0; i<devices.count(); i++){
        QVariantList sites_list = devices.at(i).getFieldValue("device_sites").toList();
        for (int j=0; j<sites_list.count(); j++){
            QVariantMap site_info = sites_list.at(j).toMap();
            if (site_info.contains("id_site")){
                if (site_info["id_site"].toInt() == m_data->getId()){
                    updateDevice(&devices.at(i));
                    break;
                }
            }
        }
    }

}

void SiteWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgSite->getInvalidFormDataLabels();

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

void SiteWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();

}

void SiteWidget::btnUpdateAccess_clicked()
{

    QJsonDocument document;
    QJsonObject base_obj;
    QJsonArray roles;

    for (int i=0; i<m_tableUsers_ids_rows.count(); i++){
        int user_id = m_tableUsers_ids_rows.keys().at(i);
        int row = m_tableUsers_ids_rows[user_id];
        QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableUsers->cellWidget(row,1));
        if (combo_roles->property("original_index").toInt() != combo_roles->currentIndex()){
            QJsonObject data_obj;
            // Ok, value was modified - must add!
            QJsonValue role = combo_roles->currentData().toString();
            data_obj.insert("id_site", m_data->getId());
            data_obj.insert("id_user", user_id);
            data_obj.insert("site_access_role", role);
            roles.append(data_obj);
        }
    }

    if (!roles.isEmpty()){
        base_obj.insert("site_access", roles);
        document.setObject(base_obj);
        postDataRequest(WEB_SITEACCESS_PATH, document.toJson());
    }



}

void SiteWidget::btnProjects_clicked()
{
    if (m_diag_editor){
        m_diag_editor->deleteLater();
    }

    m_diag_editor = new QDialog(this);
    DataListWidget* list_widget = new DataListWidget(m_comManager, TERADATA_PROJECT, m_diag_editor);
    Q_UNUSED(list_widget)

    m_diag_editor->setWindowTitle(tr("Projets"));

    m_diag_editor->open();
}

void SiteWidget::btnDevices_clicked()
{
    if (m_diag_editor){
        m_diag_editor->deleteLater();
    }
    m_diag_editor = new QDialog(this);
    DataListWidget* list_widget = new DataListWidget(m_comManager, TERADATA_DEVICE, m_diag_editor);
    Q_UNUSED(list_widget)

    m_diag_editor->setWindowTitle(tr("Appareils"));

    m_diag_editor->open();
}

void SiteWidget::btnUsers_clicked()
{
    if (m_diag_editor){
        m_diag_editor->deleteLater();
    }
    m_diag_editor = new QDialog(this);
    DataListWidget* list_widget = new DataListWidget(m_comManager, TERADATA_USER, m_diag_editor);
    Q_UNUSED(list_widget)

    m_diag_editor->setWindowTitle(tr("Utilisateurs"));

    m_diag_editor->open();
}
