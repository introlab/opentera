#include "SessionTypeWidget.h"
#include "ui_SessionTypeWidget.h"

SessionTypeWidget::SessionTypeWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::SessionTypeWidget)
{   

    ui->setupUi(this);

    setAttribute(Qt::WA_StyledBackground); //Required to set a background image

    setLimited(false);

    // Connect signals and slots
    connectSignals();

    // Query form definition
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_SESSION_TYPE));

    setData(data);

}

SessionTypeWidget::~SessionTypeWidget()
{
    if (ui)
        delete ui;
}

void SessionTypeWidget::saveData(bool signal){

    // If data is new, we request all the fields.
    QJsonDocument st_data = ui->wdgSessionType->getFormDataJson(m_data->isNew());

    postDataRequest(WEB_SESSIONTYPE_PATH, st_data.toJson());

    if (signal){
        TeraData* new_data = ui->wdgSessionType->getFormDataObject(TERADATA_SESSIONTYPE);
        *m_data = *new_data;
        delete new_data;
        emit dataWasChanged();
    }
}

void SessionTypeWidget::updateControlsState(){

    ui->wdgSessionType->setEnabled(!isWaitingOrLoading() && !m_limited);

    // Buttons update
    ui->btnSave->setEnabled(!isWaitingOrLoading());
    ui->btnUndo->setEnabled(!isWaitingOrLoading());

    ui->frameButtons->setVisible(!m_limited);

}

void SessionTypeWidget::updateFieldsValue(){
    if (m_data){
        ui->wdgSessionType->fillFormFromData(m_data->toJson());
    }
}

bool SessionTypeWidget::validateData(){
    bool valid = false;

    valid = ui->wdgSessionType->validateFormData();

    return valid;
}

void SessionTypeWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_SESSION_TYPE){
        ui->wdgSessionType->buildUiFromStructure(data);
        return;
    }
}

void SessionTypeWidget::postResultReply(QString path)
{
    // OK, data was saved!
    if (path==WEB_SESSIONTYPE_PATH){
        if (parent())
            emit closeRequest();
    }
}

void SessionTypeWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &SessionTypeWidget::processFormsReply);
    connect(m_comManager, &ComManager::postResultsOK, this, &SessionTypeWidget::postResultReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &SessionTypeWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &SessionTypeWidget::btnSave_clicked);
}

void SessionTypeWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgSessionType->getInvalidFormDataLabels();

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

void SessionTypeWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();

}
