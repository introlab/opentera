#include "GroupWidget.h"
#include "ui_GroupWidget.h"

GroupWidget::GroupWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::GroupWidget)
{   

    ui->setupUi(this);

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

void GroupWidget::updateParticipant(TeraData *participant)
{
    int id_participant = participant->getId();
    QTableWidgetItem* item;
    if (m_listParticipants_items.contains(id_participant)){
        item = m_listParticipants_items[id_participant];

    }else{
        ui->tableParticipants->setRowCount(ui->tableParticipants->rowCount()+1);
        item = new QTableWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_PARTICIPANT)),"");
        ui->tableParticipants->setItem(ui->tableParticipants->rowCount()-1, 0, item);
        m_listParticipants_items[id_participant] = item;

        QTableWidgetItem* item2 = new QTableWidgetItem("");
        item2->setTextAlignment(Qt::AlignHCenter | Qt::AlignVCenter);
        ui->tableParticipants->setItem(ui->tableParticipants->rowCount()-1, 1, item2);
        item2 = new QTableWidgetItem("");
        item2->setTextAlignment(Qt::AlignHCenter | Qt::AlignVCenter);
        ui->tableParticipants->setItem(ui->tableParticipants->rowCount()-1, 2, item2);
        item2 = new QTableWidgetItem("");
        item2->setTextAlignment(Qt::AlignHCenter | Qt::AlignVCenter);
        ui->tableParticipants->setItem(ui->tableParticipants->rowCount()-1, 3, item2);
    }

    // Update values
    item->setText(participant->getName());
    if (participant->isEnabled()){
       ui->tableParticipants->item(item->row(), 1)->setText(tr("En cours"));
       ui->tableParticipants->item(item->row(), 1)->setTextColor(Qt::green);
    }else{
       ui->tableParticipants->item(item->row(), 1)->setText(tr("Terminé"));
       ui->tableParticipants->item(item->row(), 1)->setTextColor(Qt::red);
    }
    QString date_val_str = tr("Aucune connexion");
    if (!participant->getFieldValue("participant_lastonline").isNull()){
        date_val_str = participant->getFieldValue("participant_lastonline").toDateTime().toString("dd MMMM yyyy - hh:mm");
    }
    ui->tableParticipants->item(item->row(), 2)->setText(date_val_str);
    date_val_str = tr("Aucune séance");
    if (!participant->getFieldValue("participant_lastsession").isNull()){
        QDateTime date_val = participant->getFieldValue("participant_lastsession").toDateTime();
        date_val_str = date_val.toString("dd MMMM yyyy - hh:mm");
        if (participant->isEnabled()){
            // Set background color for last session date
            QColor back_color = TeraForm::getGradientColor(0, 3, 7, static_cast<int>(date_val.daysTo(QDateTime::currentDateTime())));
            back_color.setAlphaF(0.5);
            ui->tableParticipants->item(item->row(), 3)->setBackgroundColor(back_color);
        }
    }
    ui->tableParticipants->item(item->row(), 3)->setText(date_val_str);
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

void GroupWidget::processParticipants(QList<TeraData> participants)
{
    for (TeraData participant:participants){
        if (participant.getFieldValue("id_participant_group").toInt() == m_data->getId()){
            updateParticipant(&participant);
        }
    }

    //ui->tableParticipants->resizeColumnsToContents();
}

void GroupWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &GroupWidget::processFormsReply);
    connect(m_comManager, &ComManager::postResultsOK, this, &GroupWidget::postResultReply);
    connect(m_comManager, &ComManager::participantsReceived, this, &GroupWidget::processParticipants);

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
