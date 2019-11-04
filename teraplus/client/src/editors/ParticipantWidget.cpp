#include "ParticipantWidget.h"
#include "ui_ParticipantWidget.h"

#include <QLocale>

#include "editors/DataListWidget.h"
#include "editors/SessionWidget.h"

ParticipantWidget::ParticipantWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::ParticipantWidget)
{

    m_diag_editor = nullptr;


    ui->setupUi(this);

    setAttribute(Qt::WA_StyledBackground); //Required to set a background image
    ui->btnDownloadAll->hide();
    setLimited(false);

    // Connect signals and slots
    connectSignals();

    // Query form definition
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_PARTICIPANT));
    setData(data);

    // Query sessions types
    queryDataRequest(WEB_SESSIONTYPE_PATH);

    // Query devices for that participant
    if (!m_data->isNew()){
        QUrlQuery query;
        query.addQueryItem(WEB_QUERY_ID_PARTICIPANT, QString::number(m_data->getId()));
        queryDataRequest(WEB_DEVICEPARTICIPANTINFO_PATH, query);

        // Query devices for the current site
        query.removeQueryItem(WEB_QUERY_ID_PARTICIPANT);
        query.addQueryItem(WEB_QUERY_ID_SITE, QString::number(m_data->getFieldValue("id_site").toInt()));
        queryDataRequest(WEB_DEVICESITEINFO_PATH, query);
    }
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
    connect(m_comManager, &ComManager::deviceSitesReceived, this, &ParticipantWidget::processDeviceSitesReply);
    connect(m_comManager, &ComManager::deviceParticipantsReceived, this, &ParticipantWidget::processDeviceParticipantsReply);
    connect(m_comManager, &ComManager::deleteResultsOK, this, &ParticipantWidget::deleteDataReply);
    connect(m_comManager, &ComManager::downloadCompleted, this, &ParticipantWidget::onDownloadCompleted);

    connect(ui->btnUndo, &QPushButton::clicked, this, &ParticipantWidget::btnUndo_clicked);
    connect(ui->btnSave, &QPushButton::clicked, this, &ParticipantWidget::btnSave_clicked);
    connect(ui->btnDelSession, &QPushButton::clicked, this, &ParticipantWidget::btnDeleteSession_clicked);
    connect(ui->btnAddDevice, &QPushButton::clicked, this, &ParticipantWidget::btnAddDevice_clicked);
    connect(ui->btnDelDevice, &QPushButton::clicked, this, &ParticipantWidget::btnDelDevice_clicked);
    connect(ui->btnDownloadAll, &QPushButton::clicked, this, &ParticipantWidget::btnDowloadAll_clicked);

    connect(ui->tableSessions, &QTableWidget::currentItemChanged, this, &ParticipantWidget::currentSelectedSessionChanged);
    connect(ui->tableSessions, &QTableWidget::itemDoubleClicked, this, &ParticipantWidget::displaySessionDetails);
    connect(ui->lstFilters, &QListWidget::itemChanged, this, &ParticipantWidget::currentTypeFiltersChanged);
    connect(ui->btnNextCal, &QPushButton::clicked, this, &ParticipantWidget::displayNextMonth);
    connect(ui->btnPrevCal, &QPushButton::clicked, this, &ParticipantWidget::displayPreviousMonth);

    connect(ui->lstAvailDevices, &QListWidget::currentItemChanged, this, &ParticipantWidget::currentAvailDeviceChanged);
    connect(ui->lstDevices, &QListWidget::currentItemChanged, this, &ParticipantWidget::currentDeviceChanged);
}

void ParticipantWidget::updateControlsState()
{
    ui->tabParticipantInfos->setEnabled(!m_data->isNew());
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
    QTableWidgetItem* status_item;
    QToolButton* btnDownload = nullptr;

    if (m_listSessions_items.contains(id_session)){
        // Already there, get items
       name_item = m_listSessions_items[id_session];
       date_item = ui->tableSessions->item(name_item->row(), 1);
       type_item = ui->tableSessions->item(name_item->row(), 2);
       status_item = ui->tableSessions->item(name_item->row(), 3);
       duration_item = ui->tableSessions->item(name_item->row(), 4);
       user_item = ui->tableSessions->item(name_item->row(), 5);
       if (ui->tableSessions->cellWidget(name_item->row(), 6))
           if(ui->tableSessions->cellWidget(name_item->row(), 6)->layout())
               if(ui->tableSessions->cellWidget(name_item->row(), 6)->layout()->itemAt(1))
                  btnDownload = dynamic_cast<QToolButton*>(ui->tableSessions->cellWidget(name_item->row(), 6)->layout()->itemAt(1)->widget());
       delete m_ids_sessions[id_session];
    }else{

        ui->tableSessions->setRowCount(ui->tableSessions->rowCount()+1);
        int current_row = ui->tableSessions->rowCount()-1;
        name_item = new QTableWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_SESSION)),"");
        ui->tableSessions->setItem(current_row, 0, name_item);
        date_item = new QTableWidgetItem("");
        ui->tableSessions->setItem(current_row, 1, date_item);
        type_item = new QTableWidgetItem("");
        ui->tableSessions->setItem(current_row, 2, type_item);
        status_item = new QTableWidgetItem("");
        ui->tableSessions->setItem(current_row, 3, status_item);
        duration_item = new QTableWidgetItem("");
        duration_item->setTextAlignment(Qt::AlignHCenter | Qt::AlignVCenter);
        ui->tableSessions->setItem(current_row, 4, duration_item);
        user_item = new QTableWidgetItem("");
        ui->tableSessions->setItem(current_row, 5, user_item);

        // Create action buttons
        QFrame* action_frame = new QFrame();
        QHBoxLayout* layout = new QHBoxLayout();
        layout->setContentsMargins(0,0,0,0);
        layout->setAlignment(Qt::AlignLeft);
        action_frame->setLayout(layout);

        // Delete
        QToolButton* btnDelete = new QToolButton();
        btnDelete->setIcon(QIcon(":/icons/delete.png"));
        btnDelete->setProperty("id_session", session->getId());
        btnDelete->setCursor(Qt::PointingHandCursor);
        btnDelete->setMaximumWidth(32);
        btnDelete->setToolTip(tr("Supprimer"));
        connect(btnDelete, &QToolButton::clicked, this, &ParticipantWidget::btnDeleteSession_clicked);
        layout->addWidget(btnDelete);

        // Download data
        btnDownload = new QToolButton();
        btnDownload->setIcon(QIcon(":/icons/save.png"));
        btnDownload->setProperty("id_session", session->getId());
        btnDownload->setCursor(Qt::PointingHandCursor);
        btnDownload->setMaximumWidth(32);
        btnDownload->setToolTip(tr("Télécharger les données"));
        connect(btnDownload, &QToolButton::clicked, this, &ParticipantWidget::btnDownloadSession_clicked);
        layout->addWidget(btnDownload);

        ui->tableSessions->setCellWidget(current_row, 6, action_frame);

        m_listSessions_items[id_session] = name_item;
    }
    m_ids_sessions[id_session] = new TeraData(*session);

    // Update values
    name_item->setText(session->getName());
    QDateTime session_date = session->getFieldValue("session_start_datetime").toDateTime();
    date_item->setText(session_date.toString("dd-MM-yyyy hh:mm:ss"));
    int session_type = session->getFieldValue("id_session_type").toInt();
    if (m_ids_session_types.contains(session_type)){
        type_item->setText(m_ids_session_types[session_type]->getFieldValue("session_type_name").toString());
        type_item->setForeground(QColor(m_ids_session_types[session_type]->getFieldValue("session_type_color").toString()));
    }else{
        type_item->setText("Inconnu");
    }
    duration_item->setText(QTime(0,0).addSecs(session->getFieldValue("session_duration").toInt()).toString("hh:mm:ss"));
    TeraSessionStatus::SessionStatus session_status = static_cast<TeraSessionStatus::SessionStatus>(session->getFieldValue("session_status").toInt());
    status_item->setText(TeraSessionStatus::getStatusName(session_status));
    // Set color depending on status_item
    //status_item->setTextColor(QColor(TeraSessionStatus::getStatusColor(session_status)));
    status_item->setForeground(Qt::black);
    status_item->setBackground(QColor(TeraSessionStatus::getStatusColor(session_status)));
    //QColor back_color = TeraForm::getGradientColor(3, 18, 33, static_cast<int>(session_date.daysTo(QDateTime::currentDateTime())));
    //back_color.setAlphaF(0.5);
    //date_item->setBackgroundColor(back_color);

    // Session creator
    if (!session->getFieldValue("session_creator_user").isNull())
        user_item->setText(session->getFieldValue("session_creator_user").toString());
    else if(!session->getFieldValue("session_creator_device").isNull())
        user_item->setText(tr("Appareil: ") + session->getFieldValue("session_creator_device").toString());
    else if(!session->getFieldValue("session_creator_participant").isNull())
        user_item->setText(tr("Participant: ") + session->getFieldValue("session_creator_participant").toString());
    else {
        user_item->setText(tr("Inconnu"));
    }

    // Download data
    if (btnDownload){
        btnDownload->setVisible(session->getFieldValue("session_has_device_data").toBool());
        if (session->getFieldValue("session_has_device_data").toBool())
            ui->btnDownloadAll->show();
    }

    ui->tableSessions->resizeColumnsToContents();
}

void ParticipantWidget::updateDeviceSite(TeraData *device_site)
{
    int id_device = device_site->getFieldValue("id_device").toInt();

    // Check if device is already assigned to this participant
    if (m_listDevices_items.contains(id_device)){
        // It is - return
        return;
    }

    QListWidgetItem* item;
    // Check if device already exists in available list
    if (m_listAvailDevices_items.contains(id_device)){
        item = m_listAvailDevices_items[id_device];
    }else{
        // Must create a new item
        item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)),"");
        ui->lstAvailDevices->addItem(item);
        m_listAvailDevices_items[id_device] = item;
    }

    // Update values
    item->setText(device_site->getFieldValue("device_name").toString());
    if (device_site->hasFieldName("device_available")){
        if (!device_site->getFieldValue("device_available").toBool())
            item->setIcon(QIcon("://icons/device_installed.png"));
        else
            item->setIcon(QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)));
        item->setData(Qt::UserRole, device_site->getFieldValue("device_available").toBool());
    }
}

void ParticipantWidget::updateDeviceParticipant(TeraData *device_participant)
{
    int id_device = device_participant->getFieldValue("id_device").toInt();
    QListWidgetItem* item;

    // Check if device is in the available list
    if (m_listAvailDevices_items.contains(id_device)){
        // It is - remove it from the list
        ui->lstAvailDevices->removeItemWidget(m_listAvailDevices_items[id_device]);
        delete m_listAvailDevices_items[id_device];
        m_listAvailDevices_items.remove(id_device);
    }

    // Check if device already exists in participant list
    if (m_listDevices_items.contains(id_device)){
        item = m_listDevices_items[id_device];
    }else{
        // Must create a new item
        item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)),"");
        ui->lstDevices->addItem(item);
        m_listDevices_items[id_device] = item;
        item->setData(Qt::UserRole, device_participant->getId());
    }

    // Update values
    item->setText(device_participant->getFieldValue("device_name").toString());
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
            s->setForeground(QColor(st.getFieldValue("session_type_color").toString()));
            s->setFont(QFont("Arial",10));
           /* QPixmap* pxmap = new QPixmap(8,16);
            pxmap->fill(Qt::transparent);
            QPainter* paint = new QPainter(pxmap);
            paint->setBrush(QColor(st.getFieldValue("session_type_color").toString()));
            paint->setPen(Qt::transparent);
            paint->drawRect(0,0,8,16);
            QIcon* icon = new QIcon(*pxmap);
            s->setIcon(*icon);*/
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

void ParticipantWidget::processDeviceSitesReply(QList<TeraData> device_sites)
{
    // Check if device is for us
    for(TeraData device_site:device_sites){
        if (device_site.getFieldValue("id_site").toInt() == m_data->getFieldValue("id_site").toInt()){
            // For us! Update device...
            updateDeviceSite(&device_site);
        }
    }
}

void ParticipantWidget::processDeviceParticipantsReply(QList<TeraData> device_participants)
{
    // Check if device is for us
    for(TeraData device_part:device_participants){
        if (device_part.getFieldValue("id_participant").toInt() == m_data->getId()){
            // For us! Update device...
            updateDeviceParticipant(&device_part);
        }
    }
}

void ParticipantWidget::deleteDataReply(QString path, int id)
{
    if (id==0)
        return;

    if (path == WEB_SESSIONINFO_PATH){
        // A session got deleted - check if it affects the current display
        if (m_listSessions_items.contains(id)){
            ui->tableSessions->removeRow(m_listSessions_items[id]->row());
            delete m_ids_sessions[id];
            m_ids_sessions.remove(id);
            m_listSessions_items.remove(id);
        }
    }

    if (path == WEB_DEVICEPARTICIPANTINFO_PATH){
        // A participant device association was deleted
        for (QListWidgetItem* item: m_listDevices_items.values()){
            // Check for id_device_participant, which is stored in "data" of the item
            if (item->data(Qt::UserRole).toInt() == id){
                // We found it - remove it and request update
                m_listDevices_items.remove(m_listDevices_items.key(item));
                ui->lstDevices->removeItemWidget(item);
                delete item;
                // Request refresh of available devices
                QUrlQuery query;
                query.addQueryItem(WEB_QUERY_ID_SITE, QString::number(m_data->getFieldValue("id_site").toInt()));
                queryDataRequest(WEB_DEVICESITEINFO_PATH, query);
                break;
            }
        }
    }
}

void ParticipantWidget::onDownloadCompleted(DownloadedFile *file)
{
    if (!m_comManager->hasPendingDownloads()){
        setEnabled(true);
        setReady();
        if (!m_diag_editor){
            GlobalMessageBox msgbox;
            msgbox.showInfo(tr("Téléchargement"), tr("Téléchargement terminé: ") + file->getFullFilename());
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
    // Check if the sender is a QToolButton (from the action column)
    QToolButton* action_btn = dynamic_cast<QToolButton*>(sender());
    if (action_btn){
        // Select row according to the session id of that button
        int id_session = action_btn->property("id_session").toInt();
        QTableWidgetItem* session_item = m_listSessions_items[id_session];
        ui->tableSessions->selectRow(session_item->row());
    }

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

void ParticipantWidget::btnAddDevice_clicked()
{
    QListWidgetItem* item_toadd = ui->lstAvailDevices->currentItem();

    if (!item_toadd)
        return;

    int id_device = m_listAvailDevices_items.key(item_toadd);
    if (!item_toadd->data(Qt::UserRole).toBool()){
        // Item is already assigned to at least 1 participant - show dialog.
        DeviceAssignDialog* diag = new DeviceAssignDialog(m_comManager, id_device, this);
        diag->exec();
        if (diag->result() == DeviceAssignDialog::DEVICEASSIGN_CANCEL){
            return;
        }

        if (diag->result() == DeviceAssignDialog::DEVICEASSIGN_DEASSIGN){
            // Delete all associated participants
            for (int id:diag->getDeviceParticipantsIds()){
                deleteDataRequest(WEB_DEVICEPARTICIPANTINFO_PATH, id);
            }
        }
    }

    // Add device to participant
    QJsonDocument document;
    QJsonObject base_obj;
    QJsonArray devices;

    QJsonObject item_obj;
    item_obj.insert("id_device", id_device);
    item_obj.insert("id_participant", m_data->getId());

    // Update query
    base_obj.insert("device_participant", item_obj);
    document.setObject(base_obj);
    postDataRequest(WEB_DEVICEPARTICIPANTINFO_PATH, document.toJson());
}

void ParticipantWidget::btnDelDevice_clicked()
{
    QListWidgetItem* item_todel = ui->lstDevices->currentItem();

    if (!item_todel)
        return;

    //int id_device = m_listDevices_items.key(item_todel);

    GlobalMessageBox diag;
    QMessageBox::StandardButton answer = diag.showYesNo(tr("Déassignation?"),
                                                        tr("Êtes-vous sûrs de vouloir désassigner """) + item_todel->text() + """?");
    if (answer == QMessageBox::Yes){
        // We must delete!
        m_comManager->doDelete(WEB_DEVICEPARTICIPANTINFO_PATH, item_todel->data(Qt::UserRole).toInt());
    }
}

void ParticipantWidget::btnDownloadSession_clicked()
{
    QToolButton* button = dynamic_cast<QToolButton*>(sender());
    if (button){
        // Query folder to save file
        QString save_path = QFileDialog::getExistingDirectory(this, tr("Sélectionnez un dossier pour le téléchargement"),
                                                              QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation));
        if (!save_path.isEmpty()){
            int id_session = button->property("id_session").toInt();
            QUrlQuery args;
            args.addQueryItem(WEB_QUERY_DOWNLOAD, "");
            args.addQueryItem(WEB_QUERY_ID_SESSION, QString::number(id_session));
            downloadDataRequest(save_path, WEB_DEVICEDATAINFO_PATH, args);
            setWaiting();
        }
    }
}

void ParticipantWidget::btnDowloadAll_clicked()
{
    QString save_path = QFileDialog::getExistingDirectory(this, tr("Sélectionnez un dossier pour le téléchargement"),
                                                          QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation));
    if (!save_path.isEmpty()){
        int id_participant = m_data->getId();
        QUrlQuery args;
        args.addQueryItem(WEB_QUERY_DOWNLOAD, "");
        args.addQueryItem(WEB_QUERY_ID_PARTICIPANT, QString::number(id_participant));
        downloadDataRequest(save_path, WEB_DEVICEDATAINFO_PATH, args);
        setWaiting();
    }
}

void ParticipantWidget::currentSelectedSessionChanged(QTableWidgetItem *current, QTableWidgetItem *previous)
{
    Q_UNUSED(previous)
    ui->btnDelSession->setEnabled(current);
}

void ParticipantWidget::displaySessionDetails(QTableWidgetItem *session_item)
{
    if (m_diag_editor){
        m_diag_editor->deleteLater();
    }
    m_diag_editor = new BaseDialog(this);






    int id_session = m_listSessions_items.key(ui->tableSessions->item(session_item->row(),0));
    TeraData* ses_data = m_ids_sessions[id_session];
    if (ses_data){
        SessionWidget* ses_widget = new SessionWidget(m_comManager, ses_data, nullptr);
        m_diag_editor->setCentralWidget(ses_widget);

        m_diag_editor->setWindowTitle(tr("Séance"));
        m_diag_editor->setMinimumSize(this->width(), this->height());

        connect(ses_widget, &SessionWidget::closeRequest, m_diag_editor, &QDialog::accept);

        m_diag_editor->open();
    }
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
    ui->lblMonth1->setText(QLocale::system().monthName(left_date.month()) + " " + QString::number(left_date.year()));

    left_date = left_date.addMonths(1);
    ui->calMonth2->setCurrentPage(left_date.year(),left_date.month());
    ui->lblMonth2->setText(QLocale::system().monthName(left_date.month()) + " " + QString::number(left_date.year()));

    left_date = left_date.addMonths(1);
    ui->calMonth3->setCurrentPage(left_date.year(),left_date.month());
    ui->lblMonth3->setText(QLocale::system().monthName(left_date.month()) + " " + QString::number(left_date.year()));

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

void ParticipantWidget::currentAvailDeviceChanged(QListWidgetItem *current, QListWidgetItem *previous)
{
    Q_UNUSED(previous)
    ui->btnAddDevice->setEnabled(current);
}

void ParticipantWidget::currentDeviceChanged(QListWidgetItem *current, QListWidgetItem *previous)
{
    Q_UNUSED(previous)
    ui->btnDelDevice->setEnabled(current);
}

