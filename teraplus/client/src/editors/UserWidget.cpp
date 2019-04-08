#include "UserWidget.h"
#include "ui_UserWidget.h"

#include <QtSerialPort/QSerialPortInfo>
#include <QtMultimedia/QCameraInfo>
#include <QtMultimedia/QCamera>
#include <QInputDialog>

#include <QtMultimedia/QAudioDeviceInfo>


UserWidget::UserWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::UserWidget)
{

    if (parent){
        ui->setupUi(parent);
    }else {
        ui->setupUi(this);
    }
    setAttribute(Qt::WA_StyledBackground); //Required to set a background image

    setLimited(false);

    // Connect signals and slots
    connectSignals();

    // Query forms definition
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_USER_PROFILE));
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_USER));

    // Query sites and projects
    queryDataRequest(WEB_SITEINFO_PATH);
    queryDataRequest(WEB_PROJECTINFO_PATH);

    setData(data);

}

UserWidget::~UserWidget()
{    
    if (ui)
        delete ui;
}

void UserWidget::setData(const TeraData *data){
   DataEditorWidget::setData(data);

    // Query sites and projects roles
   /* QString user_uuid = m_data->getFieldValue("user_uuid").toUuid().toString(QUuid::WithoutBraces);
    queryDataRequest(WEB_SITEINFO_PATH, QUrlQuery(QString(WEB_QUERY_USERUUID) + "=" + user_uuid));
    queryDataRequest(WEB_PROJECTINFO_PATH, QUrlQuery(QString(WEB_QUERY_USERUUID) + "=" + user_uuid));*/

}

void UserWidget::saveData(bool signal){

    // User Profile
    QString user_profile = ui->wdgProfile->getFormData(true);

    if (!ui->wdgUser->setFieldValue("user_profile", user_profile)){
        LOG_ERROR(tr("Field user_profile can't be set."), "UserWidget::saveData");
    }

    //QString user_data = ui->wdgUser->getFormData();
    // If data is new, we request all the fields.
    QJsonDocument user_data = ui->wdgUser->getFormDataJson(m_data->isNew());

    // Site access

    QJsonArray site_access = getSitesRoles();
    if (!site_access.isEmpty()){
        QJsonObject base_obj = user_data.object();
        QJsonObject base_user = base_obj["user"].toObject();
        base_user.insert("sites",site_access);
        base_obj.insert("user", base_user);
        user_data.setObject(base_obj);
    }

    // Project access
    QJsonArray project_access = getProjectsRoles();
    if (!project_access.isEmpty()){
        QJsonObject base_obj = user_data.object();
        QJsonObject base_user = base_obj["user"].toObject();
        base_user.insert("projects",project_access);
        base_obj.insert("user", base_user);
        user_data.setObject(base_obj);
    }

    //qDebug() << user_data.toJson();
    postDataRequest(WEB_USERINFO_PATH, user_data.toJson());

    if (signal)
        emit dataWasChanged();

    /*if (parent())
        emit closeRequest(); // Ask to close that editor*/
}


void UserWidget::updateControlsState(){
    ui->wdgUser->setEnabled(!isWaitingOrLoading());
    ui->wdgProfile->setEnabled(!isWaitingOrLoading());
    ui->tableSites->setEnabled(!isWaitingOrLoading());
    ui->tableProjects->setEnabled(!isWaitingOrLoading());

    // Buttons update
    ui->btnSave->setEnabled(!isWaitingOrLoading());
    ui->btnUndo->setEnabled(!isWaitingOrLoading());
    //ui->btnSave->setVisible(isEditing());
    //ui->btnUndo->setVisible(isEditing());
    // Always show save button if editing current user
    if (m_limited){
        ui->btnSave->setVisible(true);
        ui->btnUndo->setVisible(true);
    }

    // Enable access editing
    bool allow_access_edit = !m_limited;
    if (m_data){
        bool user_is_superadmin = m_data->getFieldValue("user_superadmin").toBool();
        // Super admin can't be changed - they have access to everything!
        allow_access_edit &= !user_is_superadmin;
    }
    ui->tableSites->setEnabled(allow_access_edit);
    ui->tableProjects->setEnabled(allow_access_edit);
}

void UserWidget::updateFieldsValue(){
    if (m_data && !hasPendingDataRequests()){
        if (!ui->wdgUser->formHasData())
            ui->wdgUser->fillFormFromData(m_data->toJson());
        else {
            ui->wdgUser->resetFormValues();
        }
        if (!ui->wdgProfile->formHasData())
            ui->wdgProfile->fillFormFromData(m_data->getFieldValue("user_profile").toString());
        else{
            ui->wdgProfile->resetFormValues();
        }
        resetSites();
        resetProjects();
    }
}

bool UserWidget::validateData(){
    bool valid = false;

    valid = ui->wdgUser->validateFormData();
    valid &= ui->wdgProfile->validateFormData();

    if (m_data->getId()==0){
        // New user - must check that a password is set
        if (ui->wdgUser->getFieldValue("user_password").toString().isEmpty()){
            valid = false;
        }
    }

    return valid;
}

void UserWidget::fillSites(const QList<TeraData> &sites)
{
    ui->tableSites->clearContents();
    m_tableSites_ids_rows.clear();

    for (int i=0; i<sites.count(); i++){
        ui->tableSites->setRowCount(ui->tableSites->rowCount()+1);
        int current_row = ui->tableSites->rowCount()-1;
        QTableWidgetItem* item = new QTableWidgetItem(sites.at(i).getFieldValue("site_name").toString());
        ui->tableSites->setItem(current_row,0,item);
        QComboBox* combo_roles = buildRolesComboBox();
        ui->tableSites->setCellWidget(current_row,1,combo_roles);
        if (!m_comManager->isCurrentUserSuperAdmin()){
            // Disable role selection if current user isn't admin of that site
            bool edit_enabled = m_comManager->getCurrentUserSiteRole(sites.at(i).getId()) == "admin";
            combo_roles->setEnabled(edit_enabled);
        }
        m_tableSites_ids_rows.insert(sites.at(i).getId(), current_row);
    }

    // Query sites roles
    if (m_data){
        if (!m_data->isNew()){
            QString user_uuid = m_data->getFieldValue("user_uuid").toUuid().toString(QUuid::WithoutBraces);
            queryDataRequest(WEB_SITEINFO_PATH, QUrlQuery(QString(WEB_QUERY_USERUUID) + "=" + user_uuid));
        }
    }
}

void UserWidget::updateSites(const QList<TeraData>& sites)
{
    // Don't do anything if we don't have the table data first
    if (m_tableSites_ids_rows.isEmpty())
        return;

    for (int i=0; i<sites.count(); i++){
        int site_id = sites.at(i).getId();
        if (m_tableSites_ids_rows.contains(site_id)){
            int row = m_tableSites_ids_rows[site_id];
            QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableSites->cellWidget(row,1));
            if (combo_roles){
                int index = combo_roles->findData(sites.at(i).getFieldValue("site_role").toString());
                if (index >= 0){
                    combo_roles->setCurrentIndex(index);
                }else{
                    combo_roles->setCurrentIndex(0);
                }
                combo_roles->setProperty("original_index", index);
            }

        }else{
            LOG_WARNING("Site ID " + QString::number(site_id) + " not found in table.", "UserWidget::updateSites");
        }
    }
}

QJsonArray UserWidget::getSitesRoles()
{
    QJsonArray roles;

    for (int i=0; i<m_tableSites_ids_rows.count(); i++){
        int site_id = m_tableSites_ids_rows.keys().at(i);
        int row = m_tableSites_ids_rows[site_id];
        QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableSites->cellWidget(row,1));
        //qDebug() << site_id << ": " << combo_roles->property("original_index").toInt() << " = " << combo_roles->currentIndex() << "?";
        if (combo_roles->property("original_index").toInt() != combo_roles->currentIndex()){
            QJsonObject data_obj;
            // Ok, value was modified - must add!
            QJsonValue role = combo_roles->currentData().toString();
            data_obj.insert("id_site", site_id);
            data_obj.insert("site_role", role);
            roles.append(data_obj);
        }
    }

    return roles;
}

void UserWidget::resetSites()
{
    for (int i=0; i<m_tableSites_ids_rows.count(); i++){
        int site_id = m_tableSites_ids_rows.keys().at(i);
        int row = m_tableProjects_ids_rows[site_id];
        QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableSites->cellWidget(row,1));
        combo_roles->setCurrentIndex(combo_roles->property("original_index").toInt());
    }
}

void UserWidget::fillProjects(const QList<TeraData> &projects)
{
    ui->tableProjects->clearContents();
    m_tableProjects_ids_rows.clear();


    for (int i=0; i<projects.count(); i++){
        ui->tableProjects->setRowCount(ui->tableProjects->rowCount()+1);
        int current_row = ui->tableProjects->rowCount()-1;
        QTableWidgetItem* item = new QTableWidgetItem(projects.at(i).getFieldValue("site_name").toString());
        ui->tableProjects->setItem(current_row,0,item);
        item = new QTableWidgetItem(projects.at(i).getFieldValue("project_name").toString());
        ui->tableProjects->setItem(current_row,1,item);
        QComboBox* combo_roles = buildRolesComboBox();
        ui->tableProjects->setCellWidget(current_row,2,combo_roles);
        if (!m_comManager->isCurrentUserSuperAdmin()){
            // Disable role selection if current user isn't admin of that project
            combo_roles->setEnabled(m_comManager->getCurrentUserProjectRole(projects.at(i).getId()) == "admin");
        }
        m_tableProjects_ids_rows.insert(projects.at(i).getId(), current_row);
    }

    if (m_data){
        if (!m_data->isNew()){
            QString user_uuid = m_data->getFieldValue("user_uuid").toUuid().toString(QUuid::WithoutBraces);
            queryDataRequest(WEB_PROJECTINFO_PATH, QUrlQuery(QString(WEB_QUERY_USERUUID) + "=" + user_uuid));
        }
    }
}

void UserWidget::updateProjects(const QList<TeraData>& projects)
{
    // Don't do anything if we don't have the table data first
    if (m_tableProjects_ids_rows.isEmpty())
        return;

    for (int i=0; i<projects.count(); i++){
        int project_id = projects.at(i).getId();
        if (m_tableProjects_ids_rows.contains(project_id)){
            int row = m_tableProjects_ids_rows[project_id];
            QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableProjects->cellWidget(row,2));
            if (combo_roles){
                int index = combo_roles->findData(projects.at(i).getFieldValue("project_role").toString());
                if (index >= 0){
                    combo_roles->setCurrentIndex(index);
                }else{
                    combo_roles->setCurrentIndex(0);
                }
                combo_roles->setProperty("original_index", index);
            }
        }else{
            LOG_WARNING("Project ID " + QString::number(project_id) + " not found in table.", "UserWidget::fillProjectsData");
        }
    }
}

QJsonArray UserWidget::getProjectsRoles()
{
    QJsonArray roles;

    for (int i=0; i<m_tableProjects_ids_rows.count(); i++){
        int proj_id = m_tableProjects_ids_rows.keys().at(i);
        int row = m_tableProjects_ids_rows[proj_id];
        QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableProjects->cellWidget(row,2));
        if (combo_roles->property("original_index").toInt() != combo_roles->currentIndex()){
            QJsonObject data_obj;
            // Ok, value was modified - must add!
            QJsonValue role = combo_roles->currentData().toString();
            data_obj.insert("id_project", proj_id);
            data_obj.insert("project_role", role);
            roles.append(data_obj);
        }
    }

    return roles;
}

void UserWidget::resetProjects()
{
    for (int i=0; i<m_tableProjects_ids_rows.count(); i++){
        int proj_id = m_tableProjects_ids_rows.keys().at(i);
        int row = m_tableProjects_ids_rows[proj_id];
        QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableProjects->cellWidget(row,2));
        combo_roles->setCurrentIndex(combo_roles->property("original_index").toInt());
    }
}

QComboBox *UserWidget::buildRolesComboBox()
{
    QComboBox* item_roles = new QComboBox();
    item_roles->addItem(tr("Aucun rôle"), "");
    item_roles->addItem(tr("Administrateur"), "admin");
    item_roles->addItem(tr("Utilisateur"), "user");
    item_roles->setCurrentIndex(0);

    return item_roles;
}

void UserWidget::processUsersReply(QList<TeraData> users)
{
    for (int i=0; i<users.count(); i++){
        if (users.at(i) == *m_data){
            // We found "ourself" in the list - update data.
            *m_data = users.at(i);
            updateFieldsValue();
            break;
        }
    }
    if (!hasPendingDataRequests())
        updateFieldsValue();
}

void UserWidget::processSitesReply(QList<TeraData> sites)
{
    if (m_tableSites_ids_rows.isEmpty()){
        // We don't have any site list yet - fill it with what we got.
        fillSites(sites);
    }else{
        // We want to update user roles for each site
        updateSites(sites);
    }
}

void UserWidget::processProjectsReply(QList<TeraData> projects)
{
    if (m_tableProjects_ids_rows.isEmpty()){
        // We don't have any project list yet - fill it with what we got.
        fillProjects(projects);
    }else{
        // We want to update user roles for each project
        updateProjects(projects);
    }
}

void UserWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_USER){
        ui->wdgUser->buildUiFromStructure(data);
        // Disable some widgets if we are in limited mode (editing self profile)
        if (m_limited){
            // Disable some widgets
            QWidget* item = ui->wdgUser->getWidgetForField("user_username");
            if (item) item->setEnabled(false);
            item = ui->wdgUser->getWidgetForField("user_enabled");
            if (item) item->setEnabled(false);
            item = ui->wdgUser->getWidgetForField("user_superadmin");
            if (item) item->setEnabled(false);
        }
        return;
    }

    if (form_type == WEB_FORMS_QUERY_USER_PROFILE){
        ui->wdgProfile->buildUiFromStructure(data);
        return;
    }
}

void UserWidget::postResultReply(QString path)
{
    // OK, data was saved!
    if (path==WEB_USERINFO_PATH){
        if (parent())
            emit closeRequest();
    }
}

void UserWidget::setLimited(bool limited){
    m_limited = limited;

    updateControlsState();

}

void UserWidget::connectSignals()
{
    connect(m_comManager, &ComManager::usersReceived, this, &UserWidget::processUsersReply);
    connect(m_comManager, &ComManager::sitesReceived, this, &UserWidget::processSitesReply);
    connect(m_comManager, &ComManager::projectsReceived, this, &UserWidget::processProjectsReply);
    connect(m_comManager, &ComManager::formReceived, this, &UserWidget::processFormsReply);
    connect(m_comManager, &ComManager::postResultsOK, this, &UserWidget::postResultReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &UserWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &UserWidget::btnSave_clicked);

}

void UserWidget::btnEdit_clicked()
{
    setEditing(true);
}

void UserWidget::btnDelete_clicked()
{
    undoOrDeleteData();
}

void UserWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgUser->getInvalidFormDataLabels();
        invalids.append(ui->wdgProfile->getInvalidFormDataLabels());
        if (m_data->getId()==0){
            // New user - must check that a password is set
            if (ui->wdgUser->getFieldValue("user_password").toString().isEmpty()){
                invalids.append(tr("Mot de passe"));
            }
        }

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

void UserWidget::txtPassword_textChanged(const QString &new_pass)
{
    Q_UNUSED(new_pass)
    /*if (ui->txtPassword->text().isEmpty()){
        ui->txtCPassword->setVisible(false);
        ui->txtCPassword->clear();
    }else{
        ui->txtCPassword->setVisible(true);
    }*/
}

void UserWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();


}
