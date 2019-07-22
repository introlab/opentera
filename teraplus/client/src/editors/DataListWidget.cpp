#include "DataListWidget.h"
#include "GlobalMessageBox.h"

#include "editors/UserWidget.h"
#include "editors/SiteWidget.h"
#include "editors/DeviceWidget.h"
#include "editors/SessionTypeWidget.h"

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
    m_newdata = false;

    // No copy function for now
    ui->btnCopy->hide();

    connectSignals();

    queryDataList();

}

DataListWidget::~DataListWidget()
{
    if (m_editor)
        m_editor->deleteLater();

    clearDataList();
}

void DataListWidget::updateDataInList(TeraData* data, bool select_item){

    QListWidgetItem* item = nullptr;
    bool already_present = false;

    // Check if we already have that item
    item = getItemForData(data);

    // If we don't, create a new one.
    if (!item){
        // Check if we have a new item that we could match
        item = new QListWidgetItem(data->getName(),ui->lstData);
        m_datamap[data] = item;

    }else{
        already_present = true;
        // Copy data to local object
        *m_datamap.key(item) = *data;
    }

    item->setIcon(QIcon(TeraData::getIconFilenameForDataType(data->getDataType())));
    item->setText(data->getName());
    item->setData(Qt::UserRole, data->getId());

    //Customize color and icons, if needed, according to data_type
    /*if (m_dataType==TERADATA_USER){
        if (data->getFieldValue("user_enabled").toBool())
            item->setTextColor(Qt::green);
        else {
            item->setTextColor(Qt::red);
        }
    }*/
    if (data->hasEnabledField()){
        if (data->isEnabled()){
            item->setTextColor(Qt::green);
        }else{
            item->setTextColor(Qt::red);
        }
    }

    QString color_field = TeraData::getDataTypeName(m_dataType) + "_color";
    if (data->hasFieldName(color_field)){
        item->setTextColor(QColor(data->getFieldValue(color_field).toString()));
    }

    if (select_item){
        ui->lstData->setCurrentItem(item);
    }

    if (ui->lstData->currentItem()==item){
        // Load editor
        showEditor(data);
    }

    // Delete item if it was already there (we copied what we needed)
    if (already_present){
        delete data;
    }
}

void DataListWidget::deleteDataFromList(TeraData *data)
{
    // Remove list item
    QListWidgetItem* list_item = m_datamap[data];
    if (list_item){
        delete ui->lstData->takeItem(ui->lstData->row(list_item));
        m_datamap.remove(data);
    }else{
        LOG_WARNING("Can't find ListWidgetItem for " + data->getName(), "DataListWidget::deleteDataFromList");
    }

    data->deleteLater();
}

void DataListWidget::showEditor(TeraData *data)
{
    if (m_editor){
        ui->wdgEditor->layout()->removeWidget(m_editor);
        m_editor->deleteLater();
        m_editor = nullptr;
    }

    // No data to display - return!
    if (!data)
        return;

    switch(data->getDataType()){
        case TERADATA_USER:
            m_editor = new UserWidget(m_comManager, data);
        break;
        case TERADATA_SITE:
            m_editor = new SiteWidget(m_comManager, data);
        break;
        case TERADATA_DEVICE:
            m_editor = new DeviceWidget(m_comManager, data);
        break;
        case TERADATA_SESSIONTYPE:
            m_editor = new SessionTypeWidget(m_comManager, data);
        break;
        default:
            LOG_ERROR("Unhandled datatype for editor: " + TeraData::getDataTypeName(data->getDataType()), "DataListWidget::lstData_currentItemChanged");
            return;
    }

    if (m_editor){
        connect(m_editor, &DataEditorWidget::dataWasDeleted, this, &DataListWidget::editor_dataDeleted);
        connect(m_editor, &DataEditorWidget::dataWasChanged, this, &DataListWidget::editor_dataChanged);
    }
     ui->wdgEditor->layout()->addWidget(m_editor);
}

/*void DataListWidget::itemClicked(QListWidgetItem *item){
    if (m_editor){
        if (m_editor->isEditing() && last_item!=NULL){
            lstData->setCurrentItem(last_item);
        }
    }
}*/

void DataListWidget::connectSignals()
{
    connect(m_comManager, &ComManager::waitingForReply, this, &DataListWidget::com_Waiting);
    connect(m_comManager, &ComManager::deleteResultsOK, this, &DataListWidget::deleteDataReply);

    // Connect correct signal according to the datatype
    connect(m_comManager, ComManager::getSignalFunctionForDataType(m_dataType), this, &DataListWidget::setDataList);

    connect(ui->txtSearch, &QLineEdit::textChanged, this, &DataListWidget::searchChanged);
    connect(ui->btnClear, &QPushButton::clicked, this, &DataListWidget::clearSearch);
    connect(ui->lstData, &QListWidget::currentItemChanged, this, &DataListWidget::lstData_currentItemChanged);
    connect(ui->btnNew, &QPushButton::clicked, this, &DataListWidget::newDataRequested);
    connect(ui->btnDelete, &QPushButton::clicked, this, &DataListWidget::deleteDataRequested);
}

void DataListWidget::queryDataList()
{
    QString query_path = TeraData::getPathForDataType(m_dataType);

    if (!query_path.isEmpty()){
        m_comManager->doQuery(query_path, QUrlQuery(WEB_QUERY_LIST));
    }
}

TeraData *DataListWidget::getCurrentData()
{
    if (m_datamap.key(ui->lstData->currentItem())){
        return m_datamap.key(ui->lstData->currentItem());
    }
    return nullptr;
}

QListWidgetItem *DataListWidget::getItemForData(TeraData *data)
{
    // Simple case - we have the data into direct mapping
    if (m_datamap.contains(data))
        return m_datamap[data];

    // Less simple case - the pointers are not the same, but we might be referencing an object already present.
    if (!data->isNew()){
        for (TeraData* current_data:m_datamap.keys()){
            if (*current_data == *data){
                return m_datamap[current_data];
            }
        }

        // Not found - try to find an item which is new but with the same name
        for (TeraData* current_data:m_datamap.keys()){
            if (current_data->isNew() && current_data->getName() == data->getName()){
                m_newdata=false;
                return m_datamap[current_data];
            }
        }
    }else{
        // We have a new item - try and match.
        for (TeraData* current_data:m_datamap.keys()){
            if (current_data->isNew()){
                return m_datamap[current_data];
            }
        }
    }

    // No match.
    return nullptr;

}

void DataListWidget::clearDataList(){
    ui->lstData->clear();

    for (TeraData* data:m_datamap.keys()){
        delete data;
    }
    m_datamap.clear();
}

void DataListWidget::com_Waiting(bool waiting){
    /*TeraData* current_item = getCurrentData();
    if (current_item){
        if (current_item->isNew()){
            waiting = true;
        }
    }*/
    //this->setDisabled(waiting);
    if (m_newdata)
        waiting = true;
    ui->frameItems->setDisabled(waiting);
}


void DataListWidget::deleteDataReply(QString path, int id)
{
    if (id==0)
        return;

    if (path == TeraData::getPathForDataType(m_dataType)){
        // An item that we are managing got deleted
        for (TeraData* data:m_datamap.keys()){
            if (data->getId() == id){
                deleteDataFromList(data);
                break;
            }
        }

    }
}

void DataListWidget::setDataList(QList<TeraData> list)
{
    for (int i=0; i<list.count(); i++){
        if (list.at(i).getDataType() == m_dataType){
            TeraData* item_data = new TeraData(list.at(i));
            updateDataInList(item_data);
        }
    }
}

void DataListWidget::editor_dataDeleted()
{
    // Remove data from list
    deleteDataFromList(getCurrentData());

    m_newdata = false;
    ui->lstData->setCurrentRow(-1);
    showEditor(nullptr);
}

void DataListWidget::editor_dataChanged()
{
    QListWidgetItem* item = getItemForData(m_editor->getData());

    if (item){
        item->setText(m_editor->getData()->getName());
        // Copy data to local object
        *m_datamap.key(item) = *m_editor->getData();
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


void DataListWidget::lstData_currentItemChanged(QListWidgetItem *current, QListWidgetItem *previous)
{
    Q_UNUSED(previous)
    if (!current)
        return;

    TeraData* current_data = m_datamap.keys(current).first();


    // Query full data for that data item
    m_comManager->doQuery(TeraData::getPathForDataType(current_data->getDataType()),
                          QUrlQuery(current_data->getIdFieldName() + "=" + QString::number(current_data->getId())));
}

void DataListWidget::newDataRequested()
{
    TeraData* new_data = new TeraData(m_dataType);
    new_data->setId(0);
    m_newdata = true;
    updateDataInList(new_data, true);

}

void DataListWidget::deleteDataRequested()
{
    if (!ui->lstData->currentItem())
        return;

    GlobalMessageBox diag;
    QMessageBox::StandardButton answer = diag.showYesNo(tr("Suppression?"),
                                                        tr("Êtes-vous sûrs de vouloir supprimer """) + ui->lstData->currentItem()->text() + """?");
    if (answer == QMessageBox::Yes){
        // We must delete!
        m_comManager->doDelete(TeraData::getPathForDataType(m_dataType), m_datamap.key(ui->lstData->currentItem())->getId());
    }
}

void DataListWidget::copyDataRequested()
{

}
