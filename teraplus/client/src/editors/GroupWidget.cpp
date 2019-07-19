#include "GroupWidget.h"
#include "ui_GroupWidget.h"

GroupWidget::GroupWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::GroupWidget)
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

    // Query form definition
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_GROUP));

    // Query participants of that group
    QUrlQuery query;
    query.addQueryItem(WEB_QUERY_ID_GROUP, QString::number(m_data->getId()));
    queryDataRequest(WEB_PARTICIPANTINFO_PATH, query);

    setData(data);

}

GroupWidget::~GroupWidget()
{
    if (ui)
        delete ui;
}

void GroupWidget::saveData(bool signal){

    // If data is new, we request all the fields.
    QJsonDocument group_data = ui->wdgGroup->getFormDataJson(m_data->isNew());

    postDataRequest(WEB_GROUPINFO_PATH, group_data.toJson());

    if (signal){
        TeraData* new_data = ui->wdgGroup->getFormDataObject(TERADATA_GROUP);
        *m_data = *new_data;
        delete new_data;
        emit dataWasChanged();
    }
}

void GroupWidget::updateControlsState(){

    ui->wdgGroup->setEnabled(!isWaitingOrLoading() && !m_limited);

    // Buttons update
    ui->btnSave->setEnabled(!isWaitingOrLoading());
    ui->btnUndo->setEnabled(!isWaitingOrLoading());

    ui->frameButtons->setVisible(!m_limited);

}

void GroupWidget::updateFieldsValue(){
    if (m_data){
        ui->wdgGroup->fillFormFromData(m_data->toJson());
    }
}

bool GroupWidget::validateData(){
    bool valid = false;

    valid = ui->wdgGroup->validateFormData();

    return valid;
}

void GroupWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_GROUP){
        ui->wdgGroup->buildUiFromStructure(data);
        return;
    }
}

void GroupWidget::postResultReply(QString path)
{
    // OK, data was saved!
    if (path==WEB_GROUPINFO_PATH){
        if (parent())
            emit closeRequest();
    }
}

void GroupWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &GroupWidget::processFormsReply);
    connect(m_comManager, &ComManager::postResultsOK, this, &GroupWidget::postResultReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &GroupWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &GroupWidget::btnSave_clicked);
}

void GroupWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgGroup->getInvalidFormDataLabels();

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

void GroupWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();

}
