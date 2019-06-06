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

    // Query sessions types
    queryDataRequest(WEB_SESSIONTYPES_PATH);
}

ParticipantWidget::~ParticipantWidget()
{
    delete ui;
    qDeleteAll(m_ids_session_types);
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
    connect(m_comManager, &ComManager::sessionsReceived, this, &ParticipantWidget::processSessionsReply);
    connect(m_comManager, &ComManager::sessionTypesReceived, this, &ParticipantWidget::processSessionTypesReply);

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

void ParticipantWidget::updateSession(const TeraData *session)
{
    int id_session = session->getId();

    QTableWidgetItem* name_item;
    QTableWidgetItem* date_item;
    QTableWidgetItem* type_item;
    QTableWidgetItem* duration_item;
    QTableWidgetItem* user_item;

    if (m_listSessions_items.contains(id_session)){
        // Already there, get items
       name_item = m_listSessions_items[id_session];
       date_item = ui->tableSessions->item(name_item->row(), 1);
       type_item = ui->tableSessions->item(name_item->row(), 2);
       duration_item = ui->tableSessions->item(name_item->row(), 3);
       user_item = ui->tableSessions->item(name_item->row(), 4);
    }else{
        ui->tableSessions->setRowCount(ui->tableSessions->rowCount()+1);
        name_item = new QTableWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_SESSION)),"");
        ui->tableSessions->setItem(ui->tableSessions->rowCount()-1, 0, name_item);
        date_item = new QTableWidgetItem("");
        ui->tableSessions->setItem(ui->tableSessions->rowCount()-1, 1, date_item);
        type_item = new QTableWidgetItem("");
        ui->tableSessions->setItem(ui->tableSessions->rowCount()-1, 2, type_item);
        duration_item = new QTableWidgetItem("");
        ui->tableSessions->setItem(ui->tableSessions->rowCount()-1, 3, duration_item);
        user_item = new QTableWidgetItem("");
        ui->tableSessions->setItem(ui->tableSessions->rowCount()-1, 4, user_item);

        m_listSessions_items[id_session] = name_item;
    }

    // Update values
    name_item->setText(session->getName());
    date_item->setText(session->getFieldValue("session_start_datetime").toDateTime().toString("dd-MM-yyyy hh:mm:ss"));
    int session_type = session->getFieldValue("id_session_type").toInt();
    if (m_ids_session_types.contains(session_type)){
        type_item->setText(m_ids_session_types[session_type]->getFieldValue("session_type_name").toString());
    }else{
        type_item->setText("Inconnu");
    }
    duration_item->setText(QTime(0,0).addSecs(session->getFieldValue("session_duration").toInt()).toString("hh:mm:ss"));
    user_item->setText(session->getFieldValue("session_user").toString());

    ui->tableSessions->resizeColumnsToContents();
}

void ParticipantWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_PARTICIPANT){
        ui->wdgParticipant->buildUiFromStructure(data);
        return;
    }
}

void ParticipantWidget::processSessionsReply(QList<TeraData> sessions)
{
    for(TeraData session:sessions){
        QVariantList session_parts = session.getFieldValue("session_participants_ids").toList();

        // Is that session for the current participant?
        if (session_parts.contains(m_data->getId())){
            // Add session in table or update it
            updateSession(&session);
        }else{
            // Session is not for us - ignore it.
            continue;
        }
    }
}

void ParticipantWidget::processSessionTypesReply(QList<TeraData> session_types)
{
    for (TeraData st:session_types){
        if (!m_ids_session_types.contains(st.getId())){
            m_ids_session_types[st.getId()] = new TeraData(st);
            // Add to session list
            QListWidgetItem* s = new QListWidgetItem(st.getName());
            s->setData(Qt::UserRole,st.getId());
            s->setCheckState(Qt::Checked);
            QPixmap* pxmap = new QPixmap(8,16);
            pxmap->fill(Qt::transparent);
            QPainter* paint = new QPainter(pxmap);
            paint->setBrush(QColor(st.getFieldValue("session_type_color").toString()));
            paint->setPen(Qt::transparent);
            paint->drawRect(0,0,8,16);
            QIcon* icon = new QIcon(*pxmap);
            s->setIcon(*icon);
            ui->lstFilters->addItem(s);
        }else{
            *m_ids_session_types[st.getId()] = st;
        }
    }

    // Query sessions for that participant
    if (!m_data->isNew() && m_listSessions_items.isEmpty()){
        QUrlQuery query;
        query.addQueryItem(WEB_QUERY_ID_PARTICIPANT, QString::number(m_data->getId()));
        queryDataRequest(WEB_SESSIONINFO_PATH, query);
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

