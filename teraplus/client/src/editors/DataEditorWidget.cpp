#include "DataEditorWidget.h"
#include <QApplication>

DataEditorWidget::DataEditorWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    QWidget(parent),
    m_undoing(false)
{
    m_data = nullptr;
    setData(data);
    setLoading();

    // Set ComManager pointer
    m_comManager = comMan;

    connect(m_comManager, &ComManager::networkError, this, &DataEditorWidget::comDataError);
    connect(m_comManager, &ComManager::queryResultsOK, this, &DataEditorWidget::queryDataReplyOK);
    connect(m_comManager, &ComManager::postResultsOK, this, & DataEditorWidget::postDataReplyOK);

}

DataEditorWidget::~DataEditorWidget(){
    if (m_data)
        m_data->deleteLater();
}


void DataEditorWidget::setData(const TeraData* data)
{
    if (m_data){
        m_data->deleteLater();
    }

    if (data != nullptr){
        m_data = new TeraData(*data);
    }
}

void DataEditorWidget::setLimited(bool limited){
    m_limited = limited;
    updateControlsState();
}

TeraData *DataEditorWidget::getData()
{
    return m_data;
}


/*void DataEditorWidget::setEditing(bool enabled){
    if (m_editState==STATE_WAITING)
        return; // Dont do anything if waiting

    if (m_editState==STATE_READY && enabled){
        setEditing();
        return;
    }

    if (m_editState==STATE_EDITING && !enabled){
        // Exit editing mode
        if (!m_undoing){
            // Check if data is valid
            if (validateData()){
                setWaiting();
                saveData();
            }else{
                setEditing(); // Return in editing mode
            }
        }else{
            setReady();
        }
        m_undoing = false;
    }
}*/

void DataEditorWidget::setReady(){
    if (isReady())
        return;

    m_editState = STATE_READY;
    setEnabled(true);
    setVisible(true);
    QApplication::restoreOverrideCursor();
    updateControlsState();
    m_undoing=false;
    emit stateReady();
}

void DataEditorWidget::setEditing(){
    if (isEditing())
        return;
    setEnabled(true);
    setVisible(true);
    QApplication::restoreOverrideCursor();
    m_editState = STATE_EDITING;
    updateControlsState();
    emit stateEditing();
}

void DataEditorWidget::setWaiting(){
    if (isWaiting() || isLoading())
        return;

    m_editState = STATE_WAITING;
    setEnabled(false);
    updateControlsState();
    QApplication::setOverrideCursor(Qt::WaitCursor);
    emit stateWaiting();
}

void DataEditorWidget::setLoading(){
    if (isLoading())
        return;

    m_editState = STATE_LOADING;
    setEnabled(false);
    QApplication::setOverrideCursor(Qt::BusyCursor);
    setVisible(false);
    emit stateLoading();
}

void DataEditorWidget::refreshData(){
    updateFieldsValue();
}

void DataEditorWidget::queryDataRequest(const QString &path, const QUrlQuery &query_args)
{
    QString query_name = getQueryDataName(path, query_args);
    m_requests.append(query_name);
    m_comManager->doQuery(path, query_args);
    setWaiting();
}

bool DataEditorWidget::hasPendingDataRequests()
{
    return !m_requests.isEmpty();
}

void DataEditorWidget::postDataRequest(const QString &path, const QString &json_data)
{
    QString query_name = getQueryDataName(path, QUrlQuery());
    m_requests.append(query_name);
    m_comManager->doPost(path, json_data);
    setWaiting();
}

QString DataEditorWidget::getQueryDataName(const QString &path, const QUrlQuery &query_args)
{
    QString query_name = path;
    if (!query_args.isEmpty())
        query_name += "?" + query_args.toString();
    return query_name;
}

QComboBox *DataEditorWidget::buildRolesComboBox()
{

    QComboBox* item_roles = new QComboBox();
    item_roles->addItem(tr("Aucun rôle"), "");
    item_roles->addItem(tr("Administrateur"), "admin");
    item_roles->addItem(tr("Utilisateur"), "user");
    item_roles->setCurrentIndex(0);

    return item_roles;

}

bool DataEditorWidget::isReady(){
    return m_editState == STATE_READY;
}

bool DataEditorWidget::isEditing(){
    return m_editState == STATE_EDITING;
}

bool DataEditorWidget::isWaiting(){
    return m_editState == STATE_WAITING;
}

bool DataEditorWidget::isLoading(){
    return m_editState == STATE_LOADING;
}

bool DataEditorWidget::isWaitingOrLoading()
{
    return isLoading() || isWaiting();
}

void DataEditorWidget::undoOrDeleteData(){
    //if (m_editState==STATE_EDITING){
        // If editing, undo the changes
        if (dataIsNew())
            // If a new dataset, undo = remove it
            deleteData();
        else
            undoData();

    /*}else{
        // Delete the data
        deleteData();
    }*/
}

void DataEditorWidget::queryDataReplyOK(const QString &path, const QUrlQuery &query_args)
{
    QString query_name = getQueryDataName(path, query_args);
    m_requests.removeOne(query_name);
    if (!hasPendingDataRequests())
        updateFieldsValue();

    if (m_requests.isEmpty())
        setEditing();


}

void DataEditorWidget::postDataReplyOK(const QString &path)
{
    QString query_name = getQueryDataName(path, QUrlQuery());
    m_requests.removeOne(query_name);
    if (!hasPendingDataRequests())
        updateFieldsValue();

    if (m_requests.isEmpty())
        setReady();

}

void DataEditorWidget::comDataError(QNetworkReply::NetworkError error, QString error_str)
{
    Q_UNUSED(error)
    Q_UNUSED(error_str)
    setReady();
}

void DataEditorWidget::undoData(){
    m_undoing=true;
    updateFieldsValue();
    setReady();
}

void DataEditorWidget::deleteData()
{
    emit dataWasDeleted();
}

bool DataEditorWidget::dataIsNew()
{
    if (m_data){
        return m_data->isNew();
    }
    return true;
}
