#include "UserWidget.h"
#include "ui_UserWidget.h"

#include <QtSerialPort/QSerialPortInfo>
#include <QtMultimedia/QCameraInfo>
#include <QtMultimedia/QCamera>
#include <QInputDialog>

#include <QtMultimedia/QAudioDeviceInfo>


UserWidget::UserWidget(ComManager *comMan, const TeraUser &data, QWidget *parent) :
    DataEditorWidget(comMan, parent),
    ui(new Ui::UserWidget),
    m_data(nullptr)
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
    queryDataRequest(WEB_DEFINITIONS_PATH, QUrlQuery(WEB_DEFINITIONS_PROFILE));
    queryDataRequest(WEB_DEFINITIONS_PATH, QUrlQuery(WEB_DEFINITIONS_USER));

    // Query sites and projects
    queryDataRequest(WEB_SITEINFO_PATH);
    queryDataRequest(WEB_PROJECTINFO_PATH);

    setData(data);

}

UserWidget::~UserWidget()
{    
    if (m_data)
        m_data->deleteLater();
    if (ui)
        delete ui;
}

void UserWidget::setData(const TeraUser &data){
    if (m_data)
        m_data->deleteLater();

    m_data = new TeraUser(data);

    // Query sites and projects roles
    m_usersites.clear();
    m_userprojects.clear();
    queryDataRequest(WEB_SITEINFO_PATH, QUrlQuery(QString(WEB_QUERY_USERUUID) + "=" + m_data->getUuid().toString(QUuid::WithoutBraces)));
    queryDataRequest(WEB_PROJECTINFO_PATH, QUrlQuery(QString(WEB_QUERY_USERUUID) + "=" + m_data->getUuid().toString(QUuid::WithoutBraces)));

}

TeraUser* UserWidget::getData()
{
    return m_data;
}

bool UserWidget::dataIsNew(){
    if (m_data->getId()==0)
        return true;
    else
        return false;
}

void UserWidget::saveData(bool signal){

    QString user_profile = ui->wdgProfile->getFormData(true);

    if (!ui->wdgUser->setFieldValue("user_profile", user_profile)){
        LOG_ERROR(tr("Field user_profile can't be set."), "UserWidget::saveData");
    }

    QString user_data = ui->wdgUser->getFormData();
    postDataRequest(WEB_USERINFO_PATH, user_data);

    //TODO: Site access
    //TODO: Project access

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
    ui->btnSave->setVisible(isEditing());
    ui->btnUndo->setVisible(isEditing());
    // Always show save button if editing current user
    if (m_limited){
        ui->btnSave->setVisible(true);
        ui->btnUndo->setVisible(true);
    }

    // Enable access editing
    bool allow_access_edit = m_limited;
    if (m_data)
        // Super admin can't be changed - they have access to everything!
        allow_access_edit |= m_data->getSuperAdmin();
    ui->tableSites->setEnabled(!allow_access_edit);
    ui->tableProjects->setEnabled(!allow_access_edit);
}

void UserWidget::updateFieldsValue(){
    if (m_data && !hasPendingDataRequests()){
        ui->wdgUser->fillFormFromData(m_data->toJson());
        ui->wdgProfile->fillFormFromData(m_data->getProfile());
    }
}

void UserWidget::deleteData(){

}


bool UserWidget::validateData(){
    bool valid = false;

    valid = ui->wdgUser->validateFormData();
    valid &= ui->wdgProfile->validateFormData();

    return valid;
}

void UserWidget::fillSites(const QString &sites_json)
{
    QJsonParseError json_error;

    QJsonDocument info = QJsonDocument::fromJson(sites_json.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError){
        LOG_ERROR("Unable to parse sites: " + json_error.errorString(), "UserWidget::fillSites");
        return;
    }

    ui->tableSites->clearContents();
    m_tableSites_ids_rows.clear();

    if (info.isArray()){
        QVariantList sites = info.array().toVariantList();
        for (QVariant site:sites){
            ui->tableSites->setRowCount(ui->tableSites->rowCount()+1);
            int current_row = ui->tableSites->rowCount()-1;
            if (site.canConvert(QMetaType::QVariantMap)){
                QVariantMap site_data = site.toMap();
                QTableWidgetItem* item = new QTableWidgetItem(site_data["site_name"].toString());
                ui->tableSites->setItem(current_row,0,item);
                ui->tableSites->setCellWidget(current_row,1,buildRolesComboBox());
                m_tableSites_ids_rows.insert(site_data["id_site"].toInt(), current_row);
            }
        }
    }
}

void UserWidget::fillSitesData()
{
    // Don't do anything if we don't have the table data first
    if (m_tableSites_ids_rows.isEmpty() || m_usersites.isEmpty())
        return;

    QJsonParseError json_error;

    QJsonDocument info = QJsonDocument::fromJson(m_usersites.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError){
        LOG_ERROR("Unable to parse sites: " + json_error.errorString(), "UserWidget::fillSites");
        return;
    }

     if (info.isArray()){
         QVariantList sites = info.array().toVariantList();
         for (QVariant site:sites){
             if (site.canConvert(QMetaType::QVariantMap)){
                 QVariantMap site_data = site.toMap();
                 int site_id = site_data["id_site"].toInt();
                 if (m_tableSites_ids_rows.contains(site_id)){
                     int row = m_tableSites_ids_rows[site_id];
                     QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableSites->cellWidget(row,1));
                     if (combo_roles){
                         int index = combo_roles->findData(site_data["site_role"].toString());
                         if (index >= 0){
                             combo_roles->setCurrentIndex(index);
                         }else{
                             combo_roles->setCurrentIndex(0);
                         }
                     }
                 }else{
                     LOG_WARNING("Site ID " + site_data["id_site"].toString() + " not found in table.", "UserWidget::fillSitesData");
                 }
             }
         }
     }
}

void UserWidget::fillProjects(const QString &projects_json)
{
    QJsonParseError json_error;

    QJsonDocument info = QJsonDocument::fromJson(projects_json.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError){
        LOG_ERROR("Unable to parse projects: " + json_error.errorString(), "UserWidget::fillProjects");
        return;
    }

    ui->tableProjects->clearContents();
    m_tableProjects_ids_rows.clear();

    if (info.isArray()){
        QVariantList projects = info.array().toVariantList();
        for (QVariant project:projects){
            ui->tableProjects->setRowCount(ui->tableProjects->rowCount()+1);
            int current_row = ui->tableProjects->rowCount()-1;
            if (project.canConvert(QMetaType::QVariantMap)){
                QVariantMap proj_data = project.toMap();
                QTableWidgetItem* item = new QTableWidgetItem(proj_data["site_name"].toString());
                ui->tableProjects->setItem(current_row,0,item);
                item = new QTableWidgetItem(proj_data["project_name"].toString());
                ui->tableProjects->setItem(current_row,1,item);
                ui->tableProjects->setCellWidget(current_row,2,buildRolesComboBox());
                m_tableProjects_ids_rows.insert(proj_data["id_project"].toInt(), current_row);
            }
        }
    }
}

void UserWidget::fillProjectsData()
{
    // Don't do anything if we don't have the table data first
    if (m_tableProjects_ids_rows.isEmpty() || m_userprojects.isEmpty())
        return;

    QJsonParseError json_error;

    QJsonDocument info = QJsonDocument::fromJson(m_userprojects.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError){
        LOG_ERROR("Unable to parse projects: " + json_error.errorString(), "UserWidget::fillProjectsData");
        return;
    }

    if (info.isArray()){
        QVariantList projects = info.array().toVariantList();
        for (QVariant project:projects){
            if (project.canConvert(QMetaType::QVariantMap)){
                QVariantMap proj_data = project.toMap();
                 int project_id = proj_data["id_project"].toInt();
                 if (m_tableProjects_ids_rows.contains(project_id)){
                     int row = m_tableProjects_ids_rows[project_id];
                     QComboBox* combo_roles = dynamic_cast<QComboBox*>(ui->tableProjects->cellWidget(row,2));
                     if (combo_roles){
                         int index = combo_roles->findData(proj_data["project_role"].toString());
                         if (index >= 0){
                             combo_roles->setCurrentIndex(index);
                         }else{
                             combo_roles->setCurrentIndex(0);
                         }
                     }
                 }else{
                     LOG_WARNING("Project ID " + proj_data["id_site"].toString() + " not found in table.", "UserWidget::fillProjectsData");
                 }
             }
         }
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

void UserWidget::setLimited(bool limited){
    m_limited = limited;

    //setEditing();

}

void UserWidget::connectSignals()
{
    connect(ui->btnUndo, &QPushButton::clicked, this, &UserWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &UserWidget::btnSave_clicked);
    //connect(ui->txtPassword, &QLineEdit::textChanged, this, &UserWidget::txtPassword_textChanged);

}

void UserWidget::processQueryReply(const QString &path, const QUrlQuery &query_args, const QString &data)
{
    QString query_str=query_args.toString();
    if (path == WEB_DEFINITIONS_PATH){
        if (query_str.contains(WEB_DEFINITIONS_PROFILE))
            ui->wdgProfile->buildUiFromStructure(data);
        else{
            if (query_str.contains(WEB_DEFINITIONS_USER)){
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
            }
        }
    }

    if (path == WEB_SITEINFO_PATH){
        if (query_args.hasQueryItem(WEB_QUERY_USERUUID)){
            // Specific roles for the sites
            m_usersites = data;
        }else{
            // All sites accessibles by the current user, for base lists
            fillSites(data);
        }
        fillSitesData();

    }

    if (path == WEB_PROJECTINFO_PATH){
        if (query_args.hasQueryItem(WEB_QUERY_USERUUID)){
            // Specific roles for the projects
            m_userprojects = data;
        }else{
            // All projects accessibles by the current user, for base lists
            fillProjects(data);
        }
        fillProjectsData();

    }

    if (!hasPendingDataRequests())
        updateFieldsValue();
}

void UserWidget::processPostReply(const QString &path, const QString &data)
{
    Q_UNUSED(data);
    if (path == WEB_USERINFO_PATH){
        // OK, data was saved!
        if (parent())
            emit closeRequest();
    }
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
