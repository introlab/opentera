#include "DataEditorWidget.h"

DataEditorWidget::DataEditorWidget(ComManager *comMan, QWidget *parent) :
    QWidget(parent),
    m_undoing(false)
{
    setLoading();

    // Set ComManager pointer
    m_comManager = comMan;


}

DataEditorWidget::~DataEditorWidget(){

}


void DataEditorWidget::setData(const TeraData &data)
{
    Q_UNUSED(data)
}

TeraData *DataEditorWidget::getData()
{
    return nullptr;
}


void DataEditorWidget::setEditing(bool enabled){
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
}

void DataEditorWidget::setReady(){
    if (isReady())
        return;

    m_editState = STATE_READY;
    setVisible(true);
    updateControlsState();
    m_undoing=false;
    emit stateReady();
}

void DataEditorWidget::setEditing(){
    if (isEditing())
        return;
    /*if (!isVisible())
        setVisible(true);*/
    m_editState = STATE_EDITING;
    updateControlsState();
    emit stateEditing();
}

void DataEditorWidget::setWaiting(){
    if (isWaiting())
        return;

    m_editState = STATE_WAITING;
    updateControlsState();
    emit stateWaiting();
}

void DataEditorWidget::setLoading(){
    if (isLoading())
        return;

    m_editState = STATE_LOADING;
    setVisible(false);
    emit stateLoading();
}

void DataEditorWidget::refreshData(){
    updateFieldsValue();
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

void DataEditorWidget::undoOrDeleteData(){
    if (m_editState==STATE_EDITING){
        // If editing, undo the changes
        if (dataIsNew())
            // If a new dataset, undo = remove it
            deleteData();
        else
            undoData();

    }else{
        // Delete the data
        deleteData();
    }
}

void DataEditorWidget::undoData(){
    m_undoing=true;
    updateFieldsValue();
    setReady();
}
