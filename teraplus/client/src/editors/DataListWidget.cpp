#include "DataListWidget.h"

/*DataListWidget::DataListWidget(UserInfo *currentUser, TeraDataTypes datatype, DataEditorWidget *parent) :
    DataEditorWidget(currentUser, parent),
    //parent_id(0),
    m_editor(0),
    //m_data(0),
    last_item(0)
{
    m_isDataList=true;
    //m_datalist=NULL;
    copying=false;
    searching=false;
    pending_select=false;
    pending_select_id=0;
   // m_status=STATUS_READY;

    setupUi(this);
    setAttribute(Qt::WA_StyledBackground); //Required to set a background image

    m_data_type = datatype;

    // Signals & Slots
    connect(lstData,SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem*)),this,SLOT(selectedItemChanged(QListWidgetItem*,QListWidgetItem*)));
    connect(lstData,SIGNAL(itemClicked(QListWidgetItem*)),this,SLOT(itemClicked(QListWidgetItem*)));
    connect(btnDelete,SIGNAL(clicked()),this,SLOT(deleteItemRequested()));
    connect(btnNew,SIGNAL(clicked()),this,SLOT(addItemRequested()));
    connect(btnCopy,SIGNAL(clicked()),this,SLOT(copyItemRequested()));
    connect(btnBack,SIGNAL(clicked()),this,SIGNAL(backRequested()));

    // Load default editor for the selected datatype
    switch (datatype){
     case TERADATA_USER:
        m_editor = new UserWidget(m_loggedUser, false);
        ((UserWidget*)m_editor)->setLimited(false);
        break;
    case TERADATA_KIT:
       m_editor = new UserWidget(m_loggedUser, true);
       ((UserWidget*)m_editor)->setLimited(false);
       break;
     case TERADATA_USERGROUP:
        m_editor = new UserGroupWidget(m_loggedUser);
        break;
     case TERADATA_GROUP:
        m_editor = new PatientGroupWidget(m_loggedUser);
        break;
    case TERADATA_SESSION:
       m_editor = new SessionWidget(m_loggedUser);
       connect((SessionWidget*)m_editor,SIGNAL(dataLoadingRequest(TeraDataTypes,quint64)),this,SIGNAL(dataLoadingRequest(TeraDataTypes,quint64)));
       connect((SessionWidget*)m_editor,SIGNAL(requestLiveSession(SessionType*, SessionInfo*)),this,SIGNAL(requestLiveSession(SessionType*,SessionInfo*)));
       connect(m_editor,SIGNAL(doingSession(SessionInfo*,bool,bool)),this,SIGNAL(doingSession(SessionInfo*,bool,bool)));

       break;
    case TERADATA_SESSIONTYPE:
        m_editor = new SessionTypeWidget(m_loggedUser);
        break;
    case TERADATA_TESTDEF:
        m_editor = new TestDefWidget(m_loggedUser);
        break;
     default:
        //Not supported - do nothing
        m_editor = new DefaultWidget(m_loggedUser);
        return;
        break;
    }

    connect(m_editor,SIGNAL(deleteRequest(TeraData*,TeraDataTypes)),this,SLOT(deleteItemRequested(TeraData*,TeraDataTypes)));
    //connect(m_editor,SIGNAL(startEdit(bool)),this,SLOT(editorEditMode(bool))); //Edit signal propagation
    connect(m_editor,SIGNAL(stateEditing()),this,SLOT(setEditing()));
    connect(m_editor,SIGNAL(stateWaiting()),this,SLOT(setWaiting()));
    connect(m_editor,SIGNAL(stateReady()),this,SLOT(setReady()));
    connect(m_editor,SIGNAL(listRequest(TeraDataTypes)),this,SIGNAL(listRequest(TeraDataTypes)));
    connect(m_editor,SIGNAL(limitedListRequest(TeraDataTypes)),this,SIGNAL(limitedListRequest(TeraDataTypes)));
    connect(m_editor,SIGNAL(localPatientsListRequest()),this,SIGNAL(localPatientsListRequest()));
    connect(m_editor,SIGNAL(dataLoadingRequest(TeraDataTypes,QList<SearchCriteria>)),this,SIGNAL(dataLoadingRequest(TeraDataTypes,QList<SearchCriteria>)));
    connect(m_editor,SIGNAL(cloudRequest(unsigned int)),this,SIGNAL(cloudRequest(unsigned int)));
    connect(m_editor,SIGNAL(cloudRequest(unsigned int,QList<QVariant>)),this,SIGNAL(cloudRequest(unsigned int,QList<QVariant>)));
    connect(m_editor,SIGNAL(dataWasChanged()),this,SLOT(editorDataChanged()));
    connect(m_editor,SIGNAL(setClientVariableRequest(QString,QVariant)),this,SIGNAL(setClientVariableRequest(QString,QVariant)));
    connect(m_editor,SIGNAL(statusMessage(QString,bool)),this,SIGNAL(statusMessage(QString,bool)));
    connect(m_editor,SIGNAL(dataFileRequest(DataInfo)),this,SIGNAL(dataFileRequest(DataInfo)));
    connect(m_editor,SIGNAL(saveRequest(TeraData*,TeraDataTypes)),this,SIGNAL(saveRequest(TeraData*,TeraDataTypes)));

    m_editor->setVisible(false); // Hide by default

    connect(txtSearch,SIGNAL(textChanged(QString)),this,SLOT(searchChanged(QString)));
    connect(btnClear,SIGNAL(clicked()),this,SLOT(clearSearch()));

    //QHBoxLayout* layout = new QHBoxLayout;
    //layout->addWidget(m_editor);
    //dataZone->setLayout(layout);

    //dataZone->layout()->addWidget(m_editor);
    dataZone->addWidget(m_editor);
    updateAccessibleControls();

    btnCopy->setEnabled(false);
    btnClear->setVisible(false);

    enableBackButton(false);

}*/

DataListWidget::DataListWidget(ComManager *comMan, TeraDataTypes data_type, QWidget *parent):
    QWidget(parent),
    ui(new Ui::DataListWidget),
    m_comManager(comMan),
    m_dataType(data_type)
{

    if (parent){
        ui->setupUi(parent);
    }else {
        ui->setupUi(this);
    }

    m_editor = nullptr;
    setSearching(false);

    connectSignals();

    queryDataList();

}

DataListWidget::~DataListWidget()
{
    if (m_editor)
        m_editor->deleteLater();

    clearDataList();
}

void DataListWidget::updateDataInList(TeraData* data, const bool select_item){

    QListWidgetItem* item;
    if (m_datalist.contains(data)){
        item = m_datamap[data];
    }else{
        item = new QListWidgetItem(data->getName(),ui->lstData);

        m_datalist.append(data);
        m_datamap[data] = item;

    }

    item->setIcon(QIcon(TeraData::getIconFilenameForDataType(data->getDataType())));
    item->setText(data->getName());
    item->setData(Qt::UserRole, data->getId());

    //TODO: Different color if enabled or has color property

    if (select_item){
        ui->lstData->setCurrentItem(item);
    }
}

/*void DataListWidget::itemClicked(QListWidgetItem *item){
    if (m_editor){
        if (m_editor->isEditing() && last_item!=NULL){
            lstData->setCurrentItem(last_item);
        }
    }
}*/

void DataListWidget::selectItem(quint64 id){
   /*
    if (m_datalist.isEmpty())
        return;
    if (isWaiting()){
        // Already waiting for data to be loaded - delay the new selection until then
        pending_select_id = id;
        pending_select = true;
        return;
    }
    // Find the requested id in the list
    for (int i=0;i<m_datalist.count();i++){
        if (m_datalist.at(i)->id()==id){
            //Found
            lstData->setCurrentRow(i);
            break;
        }
    }*/

}

void DataListWidget::connectSignals()
{
    connect(m_comManager, &ComManager::waitingForReply, this, &DataListWidget::com_Waiting);
    connect(m_comManager, &ComManager::queryResultsReceived, this, &DataListWidget::queryDataReply);

    connect(ui->txtSearch, &QLineEdit::textChanged, this, &DataListWidget::searchChanged);
    connect(ui->btnClear, &QPushButton::clicked, this, &DataListWidget::clearSearch);
}

void DataListWidget::queryDataList()
{
    QString query_path = TeraData::getPathForDataType(m_dataType);

    if (!query_path.isEmpty()){
        m_comManager->doQuery(query_path, QUrlQuery(WEB_QUERY_LIST));
    }
}

void DataListWidget::clearDataList(){
    ui->lstData->clear();
    m_datamap.clear();
    qDeleteAll(m_datalist);
    m_datalist.clear();
}

void DataListWidget::com_Waiting(bool waiting){
    this->setDisabled(waiting);
}

void DataListWidget::queryDataReply(const QString &path, const QUrlQuery &query_args, const QString &data)
{
    Q_UNUSED(path)
    // Build list of items from query reply
    if (query_args.hasQueryItem(WEB_QUERY_LIST)){
        clearDataList();

        QJsonParseError json_error;

        // Process reply
        QJsonDocument list_items = QJsonDocument::fromJson(data.toUtf8(), &json_error);
        if (json_error.error!= QJsonParseError::NoError){
            LOG_ERROR("Can't parse reply data.", "DataListWidget::queryDataReply");
            return;
        }

        // Browse each data
        for (QJsonValue item:list_items.array()){
            TeraData* item_data;
            // Specific case for "user" since we have a dedicated class for it
            if (m_dataType != TERADATA_USER)
                item_data = new TeraData(m_dataType, item);
            else {
                item_data = new TeraUser(item);
            }
            updateDataInList(item_data);
        }

    }else{
        // We don't have a list, but an item update.
        // TODO: Update item in list, if needed.
    }
}

void DataListWidget::searchChanged(QString new_search){
    Q_UNUSED(new_search)
    // Check if search field is empty
    if (ui->txtSearch->text().count()==0){
        setSearching(false);
        // Display back all items
        for (int i=0; i<ui->lstData->count();i++){
            ui->lstData->item(i)->setHidden(false);
        }
        if (m_editor && ui->lstData->selectedItems().count()>0)
            m_editor->setVisible(true);
        return;
    }

    if (!m_searching){
        setSearching(true);
    }

    // Apply the search filter
    QList<QListWidgetItem*> found = ui->lstData->findItems(ui->txtSearch->text(),Qt::MatchContains);
    for (int i=0; i<ui->lstData->count();i++){
        if (found.contains(ui->lstData->item(i))){
            if (ui->lstData->item(i)->isSelected()){
                if (m_editor)
                    m_editor->setVisible(true);
            }
            ui->lstData->item(i)->setHidden(false);

        }else{
            if (ui->lstData->item(i)->isSelected()){
                if (m_editor)
                    m_editor->setVisible(false);
            }
            ui->lstData->item(i)->setHidden(true);
        }
    }

}

void DataListWidget::setSearching(bool search){
    if (search){
        m_searching = true;
        ui->txtSearch->setStyleSheet("color:white;");
        ui->btnClear->setVisible(true);
    }else{
        m_searching=false;
        ui->txtSearch->setStyleSheet("color:rgba(255,255,255,50%);");
        ui->btnClear->setVisible(false);
    }
}

void DataListWidget::clearSearch(){
    ui->txtSearch->setText("");
}

