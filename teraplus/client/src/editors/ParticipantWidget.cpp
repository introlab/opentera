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
    queryDataRequest(WEB_SESSIONTYPE_PATH);
}

ParticipantWidget::~ParticipantWidget()
{
    delete ui;
    qDeleteAll(m_ids_session_types);
    qDeleteAll(m_ids_sessions);
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
    connect(m_comManager, &ComManager::deleteResultsOK, this, &ParticipantWidget::deleteDataReply);

    connect(ui->btnUndo, &QPushButton::clicked, this, &ParticipantWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &ParticipantWidget::btnSave_clicked);
    connect(ui->btnDelSession, &QPushButton::clicked, this, &ParticipantWidget::btnDeleteSession_clicked);
    connect(ui->tableSessions, &QTableWidget::currentItemChanged, this, &ParticipantWidget::currentSelectedSessionChanged);
    connect(ui->lstFilters, &QListWidget::itemChanged, this, &ParticipantWidget::currentTypeFiltersChanged);
    connect(ui->btnNextCal, &QPushButton::clicked, this, &ParticipantWidget::displayNextMonth);
    connect(ui->btnPrevCal, &QPushButton::clicked, this, &ParticipantWidget::displayPreviousMonth);
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

void ParticipantWidget::updateSession(TeraData *session)
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
        m_ids_sessions[id_session] = new TeraData(*session);
    }

    // Update values
    name_item->setText(session->getName());
    date_item->setText(session->getFieldValue("session_start_datetime").toDateTime().toString("dd-MM-yyyy hh:mm:ss"));
    int session_type = session->getFieldValue("id_session_type").toInt();
    if (m_ids_session_types.contains(session_type)){
        type_item->setText(m_ids_session_types[session_type]->getFieldValue("session_type_name").toString());
        type_item->setTextColor(QColor(m_ids_session_types[session_type]->getFieldValue("session_type_color").toString()));
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

    // Update calendar view
    currentTypeFiltersChanged(nullptr);
    updateCalendars(getMinimumSessionDate());
    ui->calMonth1->setData(m_ids_sessions.values());
    ui->calMonth2->setData(m_ids_sessions.values());
    ui->calMonth2->setData(m_ids_sessions.values());
}

void ParticipantWidget::processSessionTypesReply(QList<TeraData> session_types)
{
    ui->cmbSessionType->clear();

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

            // New session ComboBox
            ui->cmbSessionType->addItem(st.getName(), st.getId());
        }else{
            *m_ids_session_types[st.getId()] = st;
        }
    }

    ui->calMonth1->setSessionTypes(m_ids_session_types.values());
    ui->calMonth2->setSessionTypes(m_ids_session_types.values());
    ui->calMonth3->setSessionTypes(m_ids_session_types.values());

    // Query sessions for that participant
    if (!m_data->isNew() && m_listSessions_items.isEmpty()){
        QUrlQuery query;
        query.addQueryItem(WEB_QUERY_ID_PARTICIPANT, QString::number(m_data->getId()));
        queryDataRequest(WEB_SESSIONINFO_PATH, query);
    }
}

void ParticipantWidget::deleteDataReply(QString path, int id)
{
    if (id==0)
        return;

    if (path == TeraData::getPathForDataType(TERADATA_SESSION)){
        // A session got deleted - check if it affects the current display
        if (m_listSessions_items.contains(id)){
            ui->tableSessions->removeRow(m_listSessions_items[id]->row());
            delete m_ids_sessions[id];
            m_ids_sessions.remove(id);
            m_listSessions_items.remove(id);
        }
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

void ParticipantWidget::btnDeleteSession_clicked()
{
    if (!ui->tableSessions->currentItem())
        return;

    GlobalMessageBox diag;
    QTableWidgetItem* base_item = ui->tableSessions->item(ui->tableSessions->currentRow(),0);
    QMessageBox::StandardButton answer = diag.showYesNo(tr("Suppression?"),
                                                        tr("Êtes-vous sûrs de vouloir supprimer """) + base_item->text() + """?");
    if (answer == QMessageBox::Yes){
        // We must delete!
        m_comManager->doDelete(TeraData::getPathForDataType(TERADATA_SESSION), m_listSessions_items.key(base_item));
    }
}

void ParticipantWidget::currentSelectedSessionChanged(QTableWidgetItem *current, QTableWidgetItem *previous)
{
    Q_UNUSED(previous)
    ui->btnDelSession->setEnabled(current);
}

void ParticipantWidget::currentTypeFiltersChanged(QListWidgetItem *changed)
{
    Q_UNUSED(changed)
    QList<int> ids;

    for (int i=0; i<ui->lstFilters->count(); i++){
        if (ui->lstFilters->item(i)->checkState() == Qt::Checked){
            ids.append(ui->lstFilters->item(i)->data(Qt::UserRole).toInt());
        }
    }

    ui->calMonth1->setFilters(ids);
    ui->calMonth2->setFilters(ids);
    ui->calMonth3->setFilters(ids);

    // TODO: Update session tables
}

void ParticipantWidget::updateCalendars(QDate left_date){
    ui->calMonth1->setCurrentPage(left_date.year(),left_date.month());
    ui->lblMonth1->setText(QDate::longMonthName(left_date.month()) + " " + QString::number(left_date.year()));

    left_date = left_date.addMonths(1);
    ui->calMonth2->setCurrentPage(left_date.year(),left_date.month());
    ui->lblMonth2->setText(QDate::longMonthName(left_date.month()) + " " + QString::number(left_date.year()));

    left_date = left_date.addMonths(1);
    ui->calMonth3->setCurrentPage(left_date.year(),left_date.month());
    ui->lblMonth3->setText(QDate::longMonthName(left_date.month()) + " " + QString::number(left_date.year()));

    // Check if we must enable the previous month button
    QDate min_date = getMinimumSessionDate();

    if (ui->calMonth1->yearShown()==min_date.year() && ui->calMonth1->monthShown()==min_date.month())
        ui->btnPrevCal->setEnabled(false);
    else
        ui->btnPrevCal->setEnabled(true);

}

QDate ParticipantWidget::getMinimumSessionDate()
{
    QDate min_date = QDate::currentDate();
    for (TeraData* session:m_ids_sessions.values()){
        QDate session_date = session->getFieldValue("session_start_datetime").toDateTime().date();
        if (session_date < min_date)
            min_date = session_date;
    }

    return min_date;
}

void ParticipantWidget::displayNextMonth(){
    QDate new_date;
    new_date.setDate(ui->calMonth1->yearShown(), ui->calMonth1->monthShown(), 1);
    new_date = new_date.addMonths(1);

    updateCalendars(new_date);
}

void ParticipantWidget::displayPreviousMonth(){
    QDate new_date;
    new_date.setDate(ui->calMonth1->yearShown(), ui->calMonth1->monthShown(), 1);
    new_date = new_date.addMonths(-1);

    updateCalendars(new_date);
}

