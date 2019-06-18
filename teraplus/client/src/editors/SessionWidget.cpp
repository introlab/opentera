#include "SessionWidget.h"
#include "ui_SessionWidget.h"

SessionWidget::SessionWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::SessionWidget)
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
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_SESSION));

    setData(data);

}

SessionWidget::~SessionWidget()
{
    if (ui)
        delete ui;
}

void SessionWidget::saveData(bool signal){

    // If data is new, we request all the fields.
    QJsonDocument group_data = ui->wdgSession->getFormDataJson(m_data->isNew());

    postDataRequest(WEB_SESSIONINFO_PATH, group_data.toJson());

    if (signal){
        TeraData* new_data = ui->wdgSession->getFormDataObject(TERADATA_GROUP);
        *m_data = *new_data;
        delete new_data;
        emit dataWasChanged();
    }
}

void SessionWidget::updateControlsState(){

    ui->wdgSession->setEnabled(!isWaitingOrLoading() && !m_limited);

    // Buttons update
    ui->btnSave->setEnabled(!isWaitingOrLoading());
    ui->btnUndo->setEnabled(!isWaitingOrLoading());

    ui->frameButtons->setVisible(!m_limited);

}

void SessionWidget::updateFieldsValue(){
    if (m_data){
        ui->wdgSession->fillFormFromData(m_data->toJson());

        int session_status = m_data->getFieldValue("session_status").toInt();
        ui->lblStatus->setText(tr("Séance: ") + TeraSessionStatus::getStatusName(session_status));
        ui->lblStatus->setStyleSheet("background-color: " + TeraSessionStatus::getStatusColor(session_status) + "; color: black;");
    }
}

bool SessionWidget::validateData(){
    bool valid = false;

    valid = ui->wdgSession->validateFormData();

    return valid;
}

void SessionWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_SESSION){
        ui->wdgSession->buildUiFromStructure(data);
        return;
    }
}

void SessionWidget::postResultReply(QString path)
{
    // OK, data was saved!
    if (path == WEB_SESSIONINFO_PATH){
        if (parent())
            emit closeRequest();
    }
}

void SessionWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &SessionWidget::processFormsReply);
    connect(m_comManager, &ComManager::postResultsOK, this, &SessionWidget::postResultReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &SessionWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &SessionWidget::btnSave_clicked);
}

void SessionWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgSession->getInvalidFormDataLabels();

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

void SessionWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();

}
