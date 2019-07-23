#include "ProjectWidget.h"
#include "ui_ProjectWidget.h"

#include "editors/DataListWidget.h"

ProjectWidget::ProjectWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::ProjectWidget)
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
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_PROJECT));

    // Query accessible users list
    queryDataRequest(WEB_USERINFO_PATH, QUrlQuery(WEB_QUERY_LIST));

    setData(data);
}

ProjectWidget::~ProjectWidget()
{
    delete ui;

}

void ProjectWidget::saveData(bool signal)
{
    // Project data
    QJsonDocument site_data = ui->wdgProject->getFormDataJson(m_data->isNew());

    //qDebug() << user_data.toJson();
    postDataRequest(WEB_PROJECTINFO_PATH, site_data.toJson());

    if (signal){
        TeraData* new_data = ui->wdgProject->getFormDataObject(TERADATA_PROJECT);
        *m_data = *new_data;
        delete new_data;
        emit dataWasChanged();
    }
}

void ProjectWidget::setData(const TeraData *data)
{
    DataEditorWidget::setData(data);

    // Query groups & kits
    if (!dataIsNew()){
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_ID_PROJECT, QString::number(data->getFieldValue("id_project").toInt()));
        args.addQueryItem(WEB_QUERY_LIST, "");
        queryDataRequest(WEB_GROUPINFO_PATH, args);

        args = QUrlQuery();
        args.addQueryItem(WEB_QUERY_ID_SITE, QString::number(data->getFieldValue("id_site").toInt()));
        args.addQueryItem(WEB_QUERY_PARTICIPANTS, "");
        queryDataRequest(WEB_DEVICEINFO_PATH, args);
    }else{
        ui->tabProjectInfos->setEnabled(false);
    }
}

void ProjectWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &ProjectWidget::processFormsReply);
    connect(m_comManager, &ComManager::projectAccessReceived, this, &ProjectWidget::processProjectAccessReply);
    connect(m_comManager, &ComManager::usersReceived, this, &ProjectWidget::processUsersReply);
    connect(m_comManager, &ComManager::groupsReceived, this, &ProjectWidget::processGroupsReply);
    connect(m_comManager, &ComManager::devicesReceived, this, &ProjectWidget::processDevicesReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &ProjectWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &ProjectWidget::btnSave_clicked);
    connect(ui->btnUpdateRoles, &QPushButton::clicked, this, &ProjectWidget::btnUpdateAccess_clicked);
    //connect(ui->btnDevices, &QPushButton::clicked, this, &ProjectWidget::btnDevices_clicked);
    connect(ui->btnUsers, &QPushButton::clicked, this, &ProjectWidget::btnUsers_clicked);

}

void ProjectWidget::updateProjectAccess(const TeraData *access)
{
    if (m_tableUsers_ids_rows.contains(access->getFieldValue("id_user").toInt())){
        // Already there - update the user access
        int row = m_tableUsers_ids_rows[access->getFieldValue("id_user").toInt()];
        QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableUsers->cellWidget(row,1));
        if (combo_roles){
            int index = -1;
            if (access->hasFieldName("project_access_role"))
                index = combo_roles->findData(access->getFieldValue("project_access_role").toString());
            if (index >= 0){
                combo_roles->setCurrentIndex(index);
            }else{
                combo_roles->setCurrentIndex(0);
            }
            combo_roles->setProperty("original_index", index);

            if (access->hasFieldName("project_access_inherited")){
                if (access->getFieldValue("project_access_inherited").toBool()){
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
        combo_roles->setEnabled(!m_limited);
    }
}

void ProjectWidget::updateGroup(const TeraData *group)
{
    int id_group = group->getId();
    if (m_listGroups_items.contains(id_group)){
        QListWidgetItem* item = m_listGroups_items[id_group];
        item->setText(group->getName());
    }else{
        QListWidgetItem* item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_GROUP)), group->getName());
        ui->lstGroups->addItem(item);
        m_listGroups_items[id_group] = item;
    }
}

void ProjectWidget::updateDevice(const TeraData *device)
{
    int id_device = device->getId();
    QString participants_string = tr("Aucun");
    int part_count = 0;

    // Build participant string if availables
    if (device->hasFieldName("device_participants")){
        QVariantList participants = device->getFieldValue("device_participants").toList();
        participants_string = "";
        for (int i=0; i<participants.count(); i++){
            QVariantMap part_info = participants.at(i).toMap();
            // Only consider participants of that project.
            if (part_info["id_project"].toInt() == m_data->getId()){
                if (part_count>0)
                    participants_string += ", ";
                participants_string += part_info["participant_name"].toString();
                part_count++;
            }
        }
    }

    // Ignore devices without any participant in that project
    if (participants_string.isEmpty())
        return;

    if (m_listDevices_items.contains(id_device)){
        QTableWidgetItem* item = m_listDevices_items[id_device];
        item->setText(device->getName());
        ui->lstDevices->item(item->row(), 1)->setText(participants_string);
    }else{
        ui->lstDevices->setRowCount(ui->lstDevices->rowCount()+1);
        QString device_name = device->getName();
        if (device_name.isEmpty())
            device_name = tr("(Appareil sans nom)");
        QTableWidgetItem* item = new QTableWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)), device_name);
        ui->lstDevices->setItem(ui->lstDevices->rowCount()-1, 0, item);
        m_listDevices_items[id_device] = item;

        item = new QTableWidgetItem(participants_string);
        ui->lstDevices->setItem(ui->lstDevices->rowCount()-1, 1, item);
    }
}

void ProjectWidget::updateControlsState()
{
    //ui->btnDevices->setVisible(!m_limited);
    ui->btnUsers->setVisible(!m_limited);
    ui->frameButtons->setVisible(!m_limited);
    ui->btnUpdateRoles->setVisible(!m_limited);
    ui->wdgProject->setEnabled(!m_limited);

}

void ProjectWidget::updateFieldsValue()
{
    if (m_data){
        ui->wdgProject->fillFormFromData(m_data->toJson());
    }
}

bool ProjectWidget::validateData()
{
    return ui->wdgProject->validateFormData();
}

void ProjectWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_PROJECT){
        ui->wdgProject->buildUiFromStructure(data);
        return;
    }
}

void ProjectWidget::processProjectAccessReply(QList<TeraData> access)
{
    if (!m_data)
        return;

    for (int i=0; i<access.count(); i++){
        if (access.at(i).getFieldValue("id_project").toInt() == m_data->getId()){
            // Ok, we need to update information in the table
            updateProjectAccess(&access.at(i));
        }
    }
}

void ProjectWidget::processUsersReply(QList<TeraData> users)
{
    for (int i=0; i<users.count(); i++){
        updateProjectAccess(&users.at(i));
    }

    // Query access for those users
    if (m_data && !dataIsNew()){
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_ID_PROJECT, QString::number(m_data->getId()));
        queryDataRequest(WEB_PROJECTACCESS_PATH, args);
    }
}

void ProjectWidget::processGroupsReply(QList<TeraData> groups)
{
    if (!m_data)
        return;

    for (int i=0; i<groups.count(); i++){
        if (groups.at(i).getFieldValue("id_project") == m_data->getId()){
            updateGroup(&groups.at(i));
        }
    }

    /*if (isLoading()){
        // Query kits for that site (depending on projects first to have names)
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_ID_SITE, QString::number(m_data->getId()));
        args.addQueryItem(WEB_QUERY_LIST, "");
        queryDataRequest(WEB_KITINFO_PATH, args);
    }*/
}

void ProjectWidget::processDevicesReply(QList<TeraData> devices)
{
    if (!m_data)
        return;

    for (int i=0; i<devices.count(); i++){
        //if (devices.at(i).getFieldValue("id_project").toInt() == m_data->getId()){
            updateDevice(&devices.at(i));
        //}
    }

}

void ProjectWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgProject->getInvalidFormDataLabels();

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

void ProjectWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();

}

void ProjectWidget::btnUpdateAccess_clicked()
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
            data_obj.insert("id_project", m_data->getId());
            data_obj.insert("id_user", user_id);
            data_obj.insert("project_access_role", role);
            roles.append(data_obj);
        }
    }

    if (!roles.isEmpty()){
        base_obj.insert("project_access", roles);
        document.setObject(base_obj);
        postDataRequest(WEB_PROJECTACCESS_PATH, document.toJson());
    }



}

void ProjectWidget::btnDevices_clicked()
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

void ProjectWidget::btnUsers_clicked()
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
