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

void ProjectNavigator::connectSignals()
{
    connect(m_comManager, &ComManager::sitesReceived, this, &ProjectNavigator::processSitesReply);
    connect(m_comManager, &ComManager::projectsReceived, this, &ProjectNavigator::processProjectsReply);

    void (QComboBox::* comboIndexChangedSignal)(int) = &QComboBox::currentIndexChanged;
    connect(ui->cmbSites, comboIndexChangedSignal, this, &ProjectNavigator::currentSiteChanged);
    connect(ui->btnEditSite, &QPushButton::clicked, this, &ProjectNavigator::btnEditSite_clicked);
    connect(ui->treeNavigator, &QTreeWidget::currentItemChanged, this, &ProjectNavigator::currentNavItemChanged);
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
        m_projects_items[id_project] = item;
    }

    item->setText(0, project->getName());
    item->setIcon(0, QIcon(TeraData::getIconFilenameForDataType(TERADATA_PROJECT)));
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

void ProjectNavigator::newItemRequested()
{
    QAction* action = dynamic_cast<QAction*>(QObject::sender());
    if (action){
        TeraDataTypes data_type = static_cast<TeraDataTypes>(action->data().toInt());
        /*if (data_type == TERADATA_SITE){
            qDebug() << "New site";
        }*/
        if (data_type == TERADATA_PROJECT){
            qDebug() << "New project";
        }
        if (data_type == TERADATA_GROUP){
            qDebug() << "New group";
        }
        if (data_type == TERADATA_PARTICIPANT){
            qDebug() << "New participant";
        }
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

void ProjectNavigator::currentSiteChanged()
{
    m_currentSiteId = ui->cmbSites->currentData().toInt();

    // Check if user is admin of that site. If so, enable the edit button.
    ui->btnEditSite->setVisible(m_comManager->getCurrentUserSiteRole(m_currentSiteId)=="admin");

    // Clear main display
    emit dataDisplayRequest(TERADATA_NONE, 0);

    // Clear all data
    m_projects_items.clear();
    m_currentProjectId = -1;
    ui->treeNavigator->clear();

    // Query projects for that site
    QUrlQuery query;
    query.addQueryItem(WEB_QUERY_ID_SITE, QString::number(m_currentSiteId));
    query.addQueryItem(WEB_QUERY_LIST,"");
    m_comManager->doQuery(WEB_PROJECTINFO_PATH, query);
}

void ProjectNavigator::currentNavItemChanged(QTreeWidgetItem *current, QTreeWidgetItem *previous)
{
    Q_UNUSED(previous)

    if (m_projects_items.values().contains(current)){
        // We have a project
        int id = m_projects_items.key(current);
        emit dataDisplayRequest(TERADATA_PROJECT, id);
        m_currentProjectId = id;

    }
}

void ProjectNavigator::btnEditSite_clicked()
{
    emit dataDisplayRequest(TERADATA_SITE, m_currentSiteId);
}
