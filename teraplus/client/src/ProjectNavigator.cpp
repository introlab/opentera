#include "ProjectNavigator.h"
#include "ui_ProjectNavigator.h"

ProjectNavigator::ProjectNavigator(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::ProjectNavigator)
{
    ui->setupUi(this);

    m_comManager = nullptr;
    m_newItemMenu = nullptr;
    m_currentSiteId = -1;
    m_currentProjectId = -1;
    m_currentGroupId = -1;
    m_selectionHold = false;
}

ProjectNavigator::~ProjectNavigator()
{
    delete ui;
    qDeleteAll(m_newItemActions);
    if (m_newItemMenu)
        delete m_newItemMenu;
}

void ProjectNavigator::setComManager(ComManager *comMan)
{
    m_comManager = comMan;

    connectSignals();

    initUi();
}

void ProjectNavigator::initUi()
{
    // Initialize new items menu
    m_newItemMenu = new QMenu();
    QAction* new_action = addNewItemAction(TERADATA_PROJECT, tr("Projet"));
    /*addNewItemAction(TERADATA_SITE, tr("Site"));
    new_action->setDisabled(true);
    new_action = */
    new_action->setDisabled(true);
    new_action = addNewItemAction(TERADATA_GROUP, tr("Groupe"));
    new_action->setDisabled(true);
    new_action = addNewItemAction(TERADATA_PARTICIPANT, tr("Participant"));
    new_action->setDisabled(true);
    ui->btnNewItem->setMenu(m_newItemMenu);

    // Request sites
    m_comManager->doQuery(WEB_SITEINFO_PATH, QUrlQuery(WEB_QUERY_LIST));

}

int ProjectNavigator::getCurrentSiteId() const
{
    return m_currentSiteId;
}

int ProjectNavigator::getCurrentProjectId() const
{
    return m_currentProjectId;
}

void ProjectNavigator::selectItem(const TeraDataTypes &data_type, const int &id)
{
    if (data_type == TERADATA_PROJECT){
        if (m_projects_items.contains(id)){
            ui->treeNavigator->setCurrentItem(m_projects_items[id]);
        }else{
            // New item that was just added... save id for later!
            m_currentProjectId = id;
        }
        return;
    }
}

void ProjectNavigator::setOnHold(const bool &hold)
{
    m_selectionHold = hold;
}

void ProjectNavigator::connectSignals()
{
    connect(m_comManager, &ComManager::sitesReceived, this, &ProjectNavigator::processSitesReply);
    connect(m_comManager, &ComManager::projectsReceived, this, &ProjectNavigator::processProjectsReply);
    connect(m_comManager, &ComManager::groupsReceived, this, &ProjectNavigator::processGroupsReply);
    connect(m_comManager, &ComManager::participantsReceived, this, &ProjectNavigator::processParticipantsReply);

    void (QComboBox::* comboIndexChangedSignal)(int) = &QComboBox::currentIndexChanged;
    connect(ui->cmbSites, comboIndexChangedSignal, this, &ProjectNavigator::currentSiteChanged);
    connect(ui->btnEditSite, &QPushButton::clicked, this, &ProjectNavigator::btnEditSite_clicked);
    connect(ui->treeNavigator, &QTreeWidget::currentItemChanged, this, &ProjectNavigator::currentNavItemChanged);
    connect(ui->treeNavigator, &QTreeWidget::itemExpanded, this, &ProjectNavigator::navItemExpanded);
}

void ProjectNavigator::updateSite(const TeraData *site)
{
    int index = ui->cmbSites->findData(site->getId());
    if (index>=0){
        // Site already present, update infos
        ui->cmbSites->itemText(index) = site->getName();
    }else{
        // Add the site
        ui->cmbSites->addItem(site->getName(), site->getId());
    }
}

void ProjectNavigator::updateProject(const TeraData *project)
{
    int id_project = project->getId();

    // Check if project is for the current site
    if (project->getFieldValue("id_site").toInt() != m_currentSiteId){
        // Maybe that project changed site...
        if (m_projects_items.contains(id_project)){
            // It did - remove it from list.
            delete m_projects_items[id_project];
            m_projects_items.remove(id_project);
        }
        return;
    }

    QTreeWidgetItem* item;

    if (m_projects_items.contains(id_project)){
        // Project already there
        item = m_projects_items[id_project];
    }else{
        // New project - add it.
        item = new QTreeWidgetItem();
        ui->treeNavigator->addTopLevelItem(item);
        if (project->hasFieldName("project_participant_group_count")){
            if (project->getFieldValue("project_participant_group_count").toInt() > 0){
                item->setChildIndicatorPolicy(QTreeWidgetItem::ShowIndicator);
            }
        }
        m_projects_items[id_project] = item;
    }

    item->setText(0, project->getName());
    item->setIcon(0, QIcon(TeraData::getIconFilenameForDataType(TERADATA_PROJECT)));

    /*if (m_currentProjectId != id_project && m_currentProjectId >0 && !m_selectionHold){
        // Ensure correct project is selected
        ui->treeNavigator->setCurrentItem(item);
    }*/
}

void ProjectNavigator::updateGroup(const TeraData *group)
{
    int id_group = group->getId();
    int id_project = group->getFieldValue("id_project").toInt();

    // Check if current project exists
    /*if (!m_projects_items.contains(id_project)){
        LOG_WARNING("Project ID " + QString::number(id_project) + " not found for group " + group->getName(), "ProjectNavigator::updateGroup");
        return;
    }*/

    // Check if group is for the current project
    if (id_project != m_currentProjectId){
        // Maybe that group changed project...
        if (m_groups_items.contains(id_group)){
            int current_group_project = m_projects_items.key(m_groups_items[id_group]->parent());
            if (current_group_project != id_project){
                // It has - change group if available
                if (m_projects_items.contains(id_project)){
                    m_groups_items[id_group]->parent()->removeChild(m_groups_items[id_group]);
                    m_projects_items[id_project]->addChild(m_groups_items[id_group]);
                }else{
                    // Changed site also! Remove it completely from display
                    delete m_groups_items[id_group];
                    m_groups_items.remove(id_group);
                    return;
                }
            }
        }
    }

    QTreeWidgetItem* item;
    if (m_groups_items.contains(id_group)){
        // group already there
        item = m_groups_items[id_group];
    }else{
        // New group - add it.
        item = new QTreeWidgetItem();
        QTreeWidgetItem* project_item = m_projects_items[id_project];
        project_item->addChild(item);
        m_groups_items[id_group] = item;
        //project_item->setExpanded(true);
    }
    if (group->hasFieldName("group_participant_count")){
        if (group->getFieldValue("group_participant_count").toInt() > 0){
            item->setChildIndicatorPolicy(QTreeWidgetItem::ShowIndicator);
        }
    }

    item->setText(0, group->getName());
    item->setIcon(0, QIcon(TeraData::getIconFilenameForDataType(TERADATA_GROUP)));

   /* if (m_currentGroupId != id_group && m_currentGroupId >0 && !m_selectionHold){
        // Ensure correct project is selected
        ui->treeNavigator->setCurrentItem(item);
    }*/
}

void ProjectNavigator::updateParticipant(const TeraData *participant)
{
    int id_participant = participant->getId();
    int id_group = participant->getFieldValue("id_participant_group").toInt();

    QTreeWidgetItem* item;
    if (m_participants_items.contains(id_participant)){
        // Participant already there
        item = m_participants_items[id_participant];

        // Check if we need to change its group
        int id_part_group = m_groups_items.key(item->parent());
        if (id_part_group != id_group){
            // Participant is not in the correct group, change it
            QTreeWidgetItem* old_group = m_groups_items[id_part_group];
            old_group->removeChild(item);
            if (m_groups_items.contains(id_group)){
                m_groups_items[id_group]->addChild(item);
            }else{
                // Not in a displayed group, delete it
                delete item;
                return;
            }
        }
    }else{
        // New participant - add it.
        item = new QTreeWidgetItem();
        QTreeWidgetItem* group_item = m_groups_items[id_group];
        if (group_item){
            // In a group currently displayed
            group_item->addChild(item);
            m_participants_items[id_participant] = item;
        }
        //project_item->setExpanded(true);
    }
    /*if (group->hasFieldName("group_participant_count")){
        if (group->getFieldValue("group_participant_count").toInt() > 0){
            item->setChildIndicatorPolicy(QTreeWidgetItem::ShowIndicator);
        }
    }*/

    item->setText(0, participant->getName());
    item->setIcon(0, QIcon(TeraData::getIconFilenameForDataType(TERADATA_PARTICIPANT)));

}

void ProjectNavigator::updateAvailableActions()
{
    // Get user access for current site and project
    bool is_site_admin = m_comManager->getCurrentUserSiteRole(m_currentSiteId)=="admin";
    bool is_project_admin = m_comManager->getCurrentUserProjectRole(m_currentProjectId)=="admin";

    // New project
    ui->btnEditSite->setVisible(is_site_admin);
    QAction* new_project = getActionForDataType(TERADATA_PROJECT);
    if (new_project){
        new_project->setEnabled(is_site_admin);
    }

    // New group
    QAction* new_group = getActionForDataType(TERADATA_GROUP);
    if (new_group){
        new_group->setEnabled(is_project_admin);
    }

    // New participant
    QAction* new_part = getActionForDataType(TERADATA_PARTICIPANT);
    if (new_part){
        new_part->setEnabled(is_project_admin);
    }
}

QAction *ProjectNavigator::addNewItemAction(const TeraDataTypes &data_type, const QString &label)
{
    QAction* new_action = new QAction(QIcon(TeraData::getIconFilenameForDataType(data_type)), label);
    new_action->setData(data_type);
    m_newItemActions.append(new_action);

    connect(new_action, &QAction::triggered, this, &ProjectNavigator::newItemRequested);
    m_newItemMenu->addAction(new_action);

    return new_action;
}

QAction *ProjectNavigator::getActionForDataType(const TeraDataTypes &data_type)
{
    QAction* action = nullptr;

    for (int i=0; i<m_newItemActions.count(); i++){
        if (static_cast<TeraDataTypes>(m_newItemActions.at(i)->data().toInt()) == data_type){
            action = m_newItemActions.at(i);
            break;
        }
    }

    return action;
}

void ProjectNavigator::newItemRequested()
{
    QAction* action = dynamic_cast<QAction*>(QObject::sender());
    if (action){
        TeraDataTypes data_type = static_cast<TeraDataTypes>(action->data().toInt());
        emit dataDisplayRequest(data_type, 0);
    }
}

void ProjectNavigator::processSitesReply(QList<TeraData> sites)
{
    for (int i=0; i<sites.count(); i++){
        updateSite(&sites.at(i));
    }

    if (ui->cmbSites->count()==1){
        // Select the only site in the list
        ui->cmbSites->setCurrentIndex(0);
    }
}

void ProjectNavigator::processProjectsReply(QList<TeraData> projects)
{
    for (int i=0; i<projects.count(); i++){
        updateProject(&projects.at(i));
    }
}

void ProjectNavigator::processGroupsReply(QList<TeraData> groups)
{
    for (int i=0; i<groups.count(); i++){
        updateGroup(&groups.at(i));
    }
}

void ProjectNavigator::processParticipantsReply(QList<TeraData> participants)
{
    for (int i=0; i<participants.count(); i++){
        updateParticipant(&participants.at(i));
    }
}

void ProjectNavigator::currentSiteChanged()
{
    m_currentSiteId = ui->cmbSites->currentData().toInt();

    // Clear main display
    emit dataDisplayRequest(TERADATA_NONE, 0);

    // Clear all data
    m_projects_items.clear();
    m_groups_items.clear();
    m_participants_items.clear();
    m_currentProjectId = -1;
    m_currentGroupId = -1;
    ui->treeNavigator->clear();

    // Update UI according to actions availables
    updateAvailableActions();

    // Query projects for that site
    QUrlQuery query;
    query.addQueryItem(WEB_QUERY_ID_SITE, QString::number(m_currentSiteId));
    query.addQueryItem(WEB_QUERY_LIST,"");
    m_comManager->doQuery(WEB_PROJECTINFO_PATH, query);
}

void ProjectNavigator::currentNavItemChanged(QTreeWidgetItem *current, QTreeWidgetItem *previous)
{
    Q_UNUSED(previous)

    if (!current)
        return;

    current->setExpanded(true); // Will call "navItemExpanded" and expands the item

    // PROJECT
    if (m_projects_items.values().contains(current)){
        // We have a project
        //navItemExpanded(current);
        int id = m_projects_items.key(current);
        m_currentProjectId = id;
        m_currentGroupId = -1;
        emit dataDisplayRequest(TERADATA_PROJECT, m_currentProjectId);
    }

    // PARTICIPANT GROUP
    if (m_groups_items.values().contains(current)){
        // We have a participants group
        //navItemExpanded(current);
        int id = m_groups_items.key(current);
        m_currentGroupId = id;
        id = m_projects_items.key(current->parent());
        m_currentProjectId = id;
        //qDebug() << "Request to display group id: " << m_currentGroupId;
        emit dataDisplayRequest(TERADATA_GROUP, m_currentGroupId);
    }

    // PARTICIPANT
    if (m_participants_items.values().contains(current)){
        int id = m_participants_items.key(current);
        emit dataDisplayRequest(TERADATA_PARTICIPANT, id);
    }

    // Update available actions (new items)
    updateAvailableActions();
}

void ProjectNavigator::navItemExpanded(QTreeWidgetItem *item)
{
    // PROJECT
    if (m_projects_items.values().contains(item)){
        // Project: load groups for that project
        int id = m_projects_items.key(item);

        QUrlQuery query;
        query.addQueryItem(WEB_QUERY_ID_PROJECT, QString::number(id));
        query.addQueryItem(WEB_QUERY_LIST, "");
        m_comManager->doQuery(WEB_GROUPINFO_PATH, query);
    }

    // PARTICIPANT GROUP
    if (m_groups_items.values().contains(item)){
        // We have a participants group
        int id = m_groups_items.key(item);

        // Request participants for that group
        QUrlQuery query;
        query.addQueryItem(WEB_QUERY_ID_GROUP, QString::number(id));
        query.addQueryItem(WEB_QUERY_LIST, "");
        m_comManager->doQuery(WEB_PARTICIPANTINFO_PATH, query);

    }
}

void ProjectNavigator::btnEditSite_clicked()
{
    emit dataDisplayRequest(TERADATA_SITE, m_currentSiteId);
}
