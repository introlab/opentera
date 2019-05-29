#include "ParticipantWidget.h"
#include "ui_ParticipantWidget.h"

ParticipantWidget::ParticipantWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::ParticipantWidget)
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
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_PARTICIPANT));

    setData(data);
}

ParticipantWidget::~ParticipantWidget()
{
    delete ui;
}

void ParticipantWidget::saveData(bool signal)
{
    // If data is new, we request all the fields.
    QJsonDocument part_data = ui->wdgParticipant->getFormDataJson(m_data->isNew());

    postDataRequest(WEB_PARTICIPANTINFO_PATH, part_data.toJson());

    if (signal){
        TeraData* new_data = ui->wdgParticipant->getFormDataObject(TERADATA_PARTICIPANT);
        *m_data = *new_data;
        delete new_data;
        emit dataWasChanged();
    }
}

void ParticipantWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &ParticipantWidget::processFormsReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &ParticipantWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &ParticipantWidget::btnSave_clicked);
}

void ParticipantWidget::updateControlsState()
{
    ui->wdgParticipant->setEnabled(!isWaitingOrLoading() && !m_limited);

    // Buttons update
    ui->btnSave->setEnabled(!isWaitingOrLoading());
    ui->btnUndo->setEnabled(!isWaitingOrLoading());

    ui->frameButtons->setVisible(!m_limited);
}

void ParticipantWidget::updateFieldsValue()
{
    if (m_data){
        ui->wdgParticipant->fillFormFromData(m_data->toJson());
    }
}

bool ParticipantWidget::validateData()
{
    bool valid = false;

    valid = ui->wdgParticipant->validateFormData();

    return valid;
}

void ParticipantWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_PARTICIPANT){
        ui->wdgParticipant->buildUiFromStructure(data);
        return;
    }
}

void ParticipantWidget::btnSave_clicked()
{
    if (!validateData()){
        QStringList invalids = ui->wdgParticipant->getInvalidFormDataLabels();

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

void ParticipantWidget::btnUndo_clicked()
{
    undoOrDeleteData();

    if (parent())
        emit closeRequest();
}

