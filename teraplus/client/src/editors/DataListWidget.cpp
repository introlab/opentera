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
}

DataListWidget::~DataListWidget()
{
    if (m_editor)
        m_editor->deleteLater();

    qDeleteAll(m_datalist);
    m_datalist.clear();
}

void DataListWidget::setData(QList<TeraData*> *data){
    //m_datalist = data;
    qDeleteAll(m_datalist);
    m_datalist.clear();

    for (int i=0; i<data->count(); i++){
        m_datalist.append(new TeraData(*(data->at(i))));
    }
}

/*QIcon DataListWidget::getDataTypeIcon(TeraData *data){
    switch (m_data_type){
    case TERADATA_USER:
        if (data->enabled())
            return QIcon(":/pictures/icons/patient_online.png");
        else
            return QIcon(":/pictures/icons/patient_offline.png");
        break;
    case TERADATA_USERGROUP:
        return QIcon(":/pictures/icons/usergroup.png");
        break;
    case TERADATA_GROUP:
        return QIcon(":/pictures/icons/group.png");
        break;
    case TERADATA_SESSION:{
        bool has_warning = false;
        QString icon_path;
        if (qobject_cast<SessionInfo*>(data)){
            SessionInfo* session = qobject_cast<SessionInfo*>(data);
            AccessInfo access = m_loggedUser->getAccess(TERA_ACCESS_TECH);
            has_warning = access.canRead() && session->hasTechAlert();
        }
        if (data->enabled())
            icon_path = ":/pictures/icons/session_online.png";
        else
            icon_path = ":/pictures/icons/session_offline.png";

        if (has_warning){
            icon_path = icon_path.left(icon_path.length()-4) + "_warning" + icon_path.right(4);
        }
        return QIcon(icon_path);
    }
        break;
    case TERADATA_KIT:
        return QIcon(":/pictures/icons/kit.png");
        break;
    case TERADATA_SESSIONTYPE:
        return QIcon(":/pictures/icons/session.png");
        break;
    case TERADATA_TESTDEF:
        return QIcon(":/pictures/icons/test.png");
        break;
    default:
        return QIcon(":/pictures/icons/delete.png");
        break;
    }
}*/

void DataListWidget::addDataInList(TeraData* data, bool select_item){
    /*QListWidgetItem *tmp = new QListWidgetItem(ui->lstData);

    //Icon
    //tmp->setIcon(getDataTypeIcon(data));

    tmp->setText(data->getName());
    tmp->setTextAlignment(Qt::AlignLeft | Qt::AlignVCenter);
    tmp->setFlags(Qt::ItemIsSelectable | Qt::ItemIsEnabled);
    tmp->setData(Qt::UserRole,data->getId());
    //tmp->setTextColor(QColor(data->color()));

    if (select_item){
        ui->lstData->setCurrentItem(tmp);
    }*/
}

void DataListWidget::updateDataInList(int index, TeraData* data, bool select_item){
    /*if (index<0 || index>=ui->lstData->count())
        return; // Invalid index

    QListWidgetItem *tmp = ui->lstData->item(index);

    //Icon
    tmp->setIcon(getDataTypeIcon(data));

    tmp->setText(data->name());
    tmp->setData(Qt::UserRole,data->id());
    tmp->setTextColor(data->color());

    if (select_item){
        lstData->setCurrentItem(tmp);
    }*/
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
/*
void DataListWidget::searchChanged(QString new_search){
    Q_UNUSED(new_search)
    // Check if search field is empty
    if (txtSearch->text().count()==0){
        setSearching(false);
        // Display back all items
        for (int i=0; i<lstData->count();i++){
            lstData->item(i)->setHidden(false);
        }
        if (m_editor && lstData->selectedItems().count()>0)
            m_editor->setVisible(true);
        return;
    }

    if (!searching){
        setSearching(true);
    }

    // Apply the search filter
    QList<QListWidgetItem*> found = lstData->findItems(txtSearch->text(),Qt::MatchContains);
    for (int i=0; i<lstData->count();i++){
        if (found.contains(lstData->item(i))){
            if (lstData->item(i)->isSelected()){
                if (m_editor)
                    m_editor->setVisible(true);
            }
            lstData->item(i)->setHidden(false);

        }else{
            if (lstData->item(i)->isSelected()){
                if (m_editor)
                    m_editor->setVisible(false);
            }
            lstData->item(i)->setHidden(true);
        }
    }

}

void DataListWidget::setSearching(bool search){
    if (search){
        searching = true;
        txtSearch->setStyleSheet("color:white;");
        btnClear->setVisible(true);
    }else{
        searching=false;
        txtSearch->setStyleSheet("color:rgba(255,255,255,50%);");
        btnClear->setVisible(false);
    }
}

void DataListWidget::clearSearch(){
    txtSearch->setText("");
}
*/
