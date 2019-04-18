#include "SiteWidget.h"
#include "ui_SiteWidget.h"

SiteWidget::SiteWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::SiteWidget)
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

    // Query projects
    if (!dataIsNew()){
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_ID_SITE, QString::number(data->getFieldValue("id_site").toInt()));
        args.addQueryItem(WEB_QUERY_LIST, "");
        queryDataRequest(WEB_PROJECTINFO_PATH, args);
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
    connect(m_comManager, &ComManager::kitsReceived, this, &SiteWidget::processKitsReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &SiteWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &SiteWidget::btnSave_clicked);

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

void SiteWidget::updateKit(const TeraData *kit)
{
    int id_kit = kit->getId();
    QString project_name = tr("Inconnu");
    if (m_listProjects_items.contains(kit->getFieldValue("id_project").toInt()))
        project_name = m_listProjects_items[kit->getFieldValue("id_project").toInt()]->text();

    if (m_listKits_items.contains(id_kit)){
       QTableWidgetItem* item = m_listKits_items[id_kit];
       item->setText(kit->getName());

        ui->lstKits->item(item->row(), 1)->setText(project_name);
    }else{
        ui->lstKits->setRowCount(ui->lstKits->rowCount()+1);
        QTableWidgetItem* item = new QTableWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_KIT)), kit->getName());
        ui->lstKits->setItem(ui->lstKits->rowCount()-1, 0, item);
        m_listKits_items[id_kit] = item;

        item = new QTableWidgetItem(project_name);
        ui->lstKits->setItem(ui->lstKits->rowCount()-1, 1, item);
    }
}

void SiteWidget::updateControlsState()
{


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

    // Query kits for that site (depending on projects first to have names)
    QUrlQuery args;
    args.addQueryItem(WEB_QUERY_ID_SITE, QString::number(m_data->getId()));
    args.addQueryItem(WEB_QUERY_LIST, "");
    queryDataRequest(WEB_KITINFO_PATH, args);

}

void SiteWidget::processKitsReply(QList<TeraData> kits)
{
    if (!m_data)
        return;

    for (int i=0; i<kits.count(); i++){
        if (m_listProjects_items.contains(kits.at(i).getFieldValue("id_project").toInt())){
            updateKit(&kits.at(i));
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
