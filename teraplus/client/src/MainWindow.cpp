#include "MainWindow.h"
#include <QNetworkReply>

#include "ui_MainWindow.h"

#include "editors/SiteWidget.h"
#include "editors/ProjectWidget.h"
#include "editors/GroupWidget.h"
#include "editors/ParticipantWidget.h"

MainWindow::MainWindow(ComManager *com_manager, QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    m_comManager = com_manager;
    m_diag_editor = nullptr;
    m_data_editor = nullptr;
    m_download_dialog = nullptr;
    m_waiting_for_data_type = TERADATA_NONE;
    m_currentMessage.setMessage(Message::MESSAGE_NONE,"");

    // Initial UI state
    initUi();

    // Connect signals
    connectSignals();

    // Update user in case we already have it
    updateCurrentUser();
}

MainWindow::~MainWindow()
{
    delete ui;
    delete m_loadingIcon;
    if (m_data_editor)
        m_data_editor->deleteLater();

}

void MainWindow::connectSignals()
{
    connect(m_comManager, &ComManager::currentUserUpdated, this, &MainWindow::updateCurrentUser);
    connect(m_comManager, &ComManager::networkError, this, &MainWindow::com_networkError);
    connect(m_comManager, &ComManager::serverError, this, &MainWindow::com_serverError);
    connect(m_comManager, &ComManager::waitingForReply, this, &MainWindow::com_waitingForReply);
    connect(m_comManager, &ComManager::postResultsOK, this, &MainWindow::com_postReplyOK);
    connect(m_comManager, &ComManager::dataReceived, this, &MainWindow::processGenericDataReply);
    connect(m_comManager, &ComManager::deleteResultsOK, this, &MainWindow::com_deleteResultsOK);
    connect(m_comManager, &ComManager::downloadProgress, this, &MainWindow::com_downloadProgress);
    connect(m_comManager, &ComManager::downloadCompleted, this, &MainWindow::com_downloadCompleted);

    connect(&m_msgTimer, &QTimer::timeout, this, &MainWindow::showNextMessage);

    connect(ui->wdgMainMenu, &ProjectNavigator::dataDisplayRequest, this, &MainWindow::dataDisplayRequested);
    connect(ui->wdgMainMenu, &ProjectNavigator::dataDeleteRequest, this, &MainWindow::dataDeleteRequested);
}

void MainWindow::initUi()
{
    // Setup messages
    ui->frameMessages->hide();
    m_msgTimer.setSingleShot(true);
    m_msgTimer.setInterval(8000);

    // Disable docker titles
    ui->dockerTop->setTitleBarWidget(new QWidget());
    ui->dockerLeft->setTitleBarWidget(new QWidget());

    // Setup loading icon animation
    m_loadingIcon = new QMovie("://status/loading.gif");
    ui->icoLoading->setMovie(m_loadingIcon);
    ui->icoLoading->hide();

    // Setup main menu
    ui->wdgMainMenu->setComManager(m_comManager);

}

void MainWindow::showDataEditor(const TeraDataTypes &data_type, const TeraData*data)
{
    if (m_data_editor){
        m_data_editor->deleteLater();
        m_data_editor = nullptr;
    }

    if (data_type == TERADATA_NONE || data == nullptr){
        return;
    }

    if (data_type == TERADATA_SITE){
        m_data_editor = new SiteWidget(m_comManager, data);
        m_data_editor->setLimited(m_comManager->getCurrentUserSiteRole(data->getId()) != "admin" && data->getId()>0);
    }

    if (data_type == TERADATA_PROJECT){
        m_data_editor = new ProjectWidget(m_comManager, data);
        m_data_editor->setLimited(m_comManager->getCurrentUserProjectRole(data->getId()) != "admin" && data->getId()>0);
    }

    if (data_type == TERADATA_GROUP){
        m_data_editor = new GroupWidget(m_comManager, data);
        bool limited = false;
        if (data->hasFieldName("id_project")){
            limited = m_comManager->getCurrentUserProjectRole(data->getFieldValue("id_project").toInt()) != "admin" && data->getId()>0;
        }
        m_data_editor->setLimited(limited);
    }

    if (data_type == TERADATA_PARTICIPANT){
        m_data_editor = new ParticipantWidget(m_comManager, data);
        bool limited = true;
        if (data->hasFieldName("id_project")){
            limited = m_comManager->getCurrentUserProjectRole(data->getFieldValue("id_project").toInt()) != "admin";
        }
        if (data->getId()==0)
            limited = false;
        m_data_editor->setLimited(limited);

    }

    if (m_data_editor){
        ui->wdgMainTop->layout()->addWidget(m_data_editor);
        connect(m_data_editor, &DataEditorWidget::dataWasDeleted, this, &MainWindow::dataEditorCancelled);
    }else{
        LOG_ERROR("Unhandled data editor: " + TeraData::getPathForDataType(data_type), "MainWindow::showDataEditor");
    }
}

void MainWindow::showNextMessage()
{
    m_loadingIcon->stop();
    ui->frameMessages->hide();
    m_msgTimer.stop();
    if (m_messages.isEmpty()){
        m_currentMessage.setMessage(Message::MESSAGE_NONE,"");
        return;
    }

    m_currentMessage = m_messages.takeFirst();

    QString background_color = "rgba(128,128,128,50%)";
    QString icon_path = "";

    switch(m_currentMessage.getMessageType()){
    case Message::MESSAGE_OK:
        background_color = "rgba(0,255,0,50%)";
        ui->icoMessage->setPixmap(QPixmap("://icons/ok.png"));
        break;
    case Message::MESSAGE_ERROR:
        background_color = "rgba(255,0,0,50%)";
        ui->icoMessage->setPixmap(QPixmap("://icons/error.png"));
        break;
    case Message::MESSAGE_WARNING:
        background_color = "rgba(255,85,0,50%)";
        ui->icoMessage->setPixmap(QPixmap("://icons/warning.png"));
        break;
    case Message::MESSAGE_WORKING:
        background_color = "rgba(128,128,128,50%)";
        ui->icoMessage->setMovie(m_loadingIcon);
        m_loadingIcon->start();
        break;
    default:
        break;
    }
    ui->frameMessages->setStyleSheet("QWidget#frameMessages{background-color: " + background_color + ";}");
    ui->lblMessage->setText(m_currentMessage.getMessageText());
    if (m_currentMessage.getMessageType() != Message::MESSAGE_ERROR && m_currentMessage.getMessageType()!=Message::MESSAGE_NONE)
        m_msgTimer.start();

    QPropertyAnimation *animate = new QPropertyAnimation(ui->frameMessages,"windowOpacity",this);
    animate->setDuration(1000);
    animate->setStartValue(0.0);
    animate->setKeyValueAt(0.1, 0.8);
    animate->setKeyValueAt(0.9, 0.8);
    animate->setEndValue(0.0);
    animate->start(QAbstractAnimation::DeleteWhenStopped);
    ui->frameMessages->show();
}

void MainWindow::editorDialogFinished()
{
    m_diag_editor->deleteLater();
    m_diag_editor = nullptr;

    // Enable selection in the project manager
    ui->wdgMainMenu->setOnHold(false);
}

void MainWindow::dataDisplayRequested(TeraDataTypes data_type, int data_id)
{
    if (data_type == TERADATA_NONE){
        // Clear data display
        showDataEditor(TERADATA_NONE, nullptr);
        return;
    }

    if (data_id == 0){
        ui->wdgMainMenu->setEnabled(false);
        TeraData* new_data = new TeraData(data_type);
        new_data->setId(0);

        // Set default values for new data
        if (data_type == TERADATA_PROJECT)
            new_data->setFieldValue("id_site", ui->wdgMainMenu->getCurrentSiteId());

        if (data_type == TERADATA_GROUP){
            new_data->setFieldValue("id_project", ui->wdgMainMenu->getCurrentProjectId());
        }

        if (data_type == TERADATA_PARTICIPANT){
            new_data->setFieldValue("id_participant_group", ui->wdgMainMenu->getCurrentGroupId());
        }

        showDataEditor(data_type, new_data);
        return;
    }

    // Set flag to wait for that specific data type
    if (m_waiting_for_data_type != TERADATA_NONE)
        LOG_WARNING("Request for new data for editor, but still waiting on previous one!", "MainWindow::dataDisplayRequested");
    m_waiting_for_data_type = data_type;

    QUrlQuery query;
    query.addQueryItem(WEB_QUERY_ID, QString::number(data_id));
    m_comManager->doQuery(TeraData::getPathForDataType(data_type), query);

}

void MainWindow::dataDeleteRequested(TeraDataTypes data_type, int data_id)
{
    /*if (m_waiting_for_data_type != TERADATA_NONE)
        LOG_WARNING("Request to delete, but still waiting on previous result!", "MainWindow::dataDeleteRequested");
    m_waiting_for_data_type = data_type;*/

    m_comManager->doDelete(TeraData::getPathForDataType(data_type), data_id);
}

void MainWindow::dataEditorCancelled()
{
    showDataEditor(TERADATA_NONE, nullptr);
    ui->wdgMainMenu->setEnabled(true);
}

void MainWindow::updateCurrentUser()
{
    if (m_comManager->getCurrentUser().hasFieldName("user_name")){
        // Ok, we have a user to update.
        ui->lblUser->setText(m_comManager->getCurrentUser().getName());
        ui->btnConfig->setVisible(m_comManager->getCurrentUser().getFieldValue("user_superadmin").toBool());
    }
}

void MainWindow::processGenericDataReply(QList<TeraData> datas)
{
    if (datas.isEmpty())
        return;

    TeraDataTypes item_data_type = datas.first().getDataType();

    if (m_data_editor){
        if (m_data_editor->getData()->getDataType() == item_data_type && m_data_editor->getData()->getId()==0){
            // New item that was saved?
            if (m_data_editor->getData()->getName() == datas.first().getName()){
                // Yes, it is - close data editor
                showDataEditor(TERADATA_NONE, nullptr);
                ui->wdgMainMenu->setEnabled(true);
            }
        }
    }

    if (m_waiting_for_data_type != item_data_type)
        return;

    m_waiting_for_data_type = TERADATA_NONE;

    // Show editor
    showDataEditor(item_data_type, &datas.first());

}


void MainWindow::com_serverError(QAbstractSocket::SocketError error, QString error_msg)
{
    Q_UNUSED(error)
    addMessage(Message::MESSAGE_ERROR, error_msg);
}

void MainWindow::com_networkError(QNetworkReply::NetworkError error, QString error_msg)
{
    addMessage(Message::MESSAGE_ERROR, tr("Erreur ") + QString::number(error) + ": " + error_msg);
}

void MainWindow::com_waitingForReply(bool waiting)
{
    /*if (waiting){
        if (!hasWaitingMessage())
            addMessage(Message::MESSAGE_WORKING, "");
     }else{
        if (m_currentMessage.getMessageType()==Message::MESSAGE_WORKING)
            showNextMessage();
    }*/
    ui->icoLoading->setVisible(waiting);
    if (waiting)
        m_loadingIcon->start();
    else {
        m_loadingIcon->stop();
    }
    ui->btnEditUser->setEnabled(!waiting);
    ui->btnConfig->setEnabled(!waiting);
    ui->wdgMainMenu->setEnabled(!waiting);
}

void MainWindow::com_postReplyOK()
{
    addMessage(Message::MESSAGE_OK, tr("Données sauvegardées."));
}

void MainWindow::com_deleteResultsOK(QString path, int id)
{
    ui->wdgMainMenu->removeItem(TeraData::getDataTypeFromPath(path), id);
}

void MainWindow::com_downloadProgress(DownloadedFile *file)
{
    if (!m_download_dialog){
        // New download request - create dialog and add file
        m_download_dialog = new DownloadProgressDialog(this);
        m_download_dialog->show();
    }
    m_download_dialog->updateDownloadedFile(file);
}

void MainWindow::com_downloadCompleted(DownloadedFile *file)
{
    if (m_download_dialog){
        if (m_download_dialog->downloadFileCompleted(file)){
            // If we are here, no more downloads are pending. Close download dialog.
            m_download_dialog->close();
            m_download_dialog->deleteLater();
            m_download_dialog = nullptr;
        }
    }
}

void MainWindow::on_btnLogout_clicked()
{
    emit logout_request();
}

void MainWindow::addMessage(Message::MessageType msg_type, QString msg)
{
    Message message(msg_type, msg);
    addMessage(message);
}

void MainWindow::addMessage(const Message &msg)
{
    m_messages.append(msg);

    if (ui->frameMessages->isHidden())
        showNextMessage();
}

bool MainWindow::hasWaitingMessage()
{
    for (Message msg:m_messages){
        if (msg.getMessageType()==Message::MESSAGE_WORKING)
            return true;
    }
    return false;
}

void MainWindow::on_btnCloseMessage_clicked()
{
    showNextMessage();
}

void MainWindow::on_btnEditUser_clicked()
{
    if (m_diag_editor){
        m_diag_editor->deleteLater();
    }

    // Hold all selection from happening in the project manager
    ui->wdgMainMenu->setOnHold(true);

    m_diag_editor = new QDialog(this);
    UserWidget* user_editor = new UserWidget(m_comManager, &(m_comManager->getCurrentUser()), m_diag_editor);
    user_editor->setLimited(true);
    connect(user_editor, &UserWidget::closeRequest, m_diag_editor, &QDialog::accept);
    connect(m_diag_editor, &QDialog::finished, this, &MainWindow::editorDialogFinished);

    m_diag_editor->setWindowTitle(tr("Votre compte"));

    m_diag_editor->open();
}

void MainWindow::on_btnConfig_clicked()
{
    if (m_diag_editor){
        m_diag_editor->deleteLater();
    }

    // Hold all selection from happening in the project manager
    ui->wdgMainMenu->setOnHold(true);

    m_diag_editor = new QDialog(this);
    ConfigWidget* config_editor = new ConfigWidget(m_comManager, m_diag_editor);
    m_diag_editor->setFixedSize(size().width()-50, size().height()-150);
    //m_diag_editor->move(25,75);

    connect(m_diag_editor, &QDialog::finished, this, &MainWindow::editorDialogFinished);
    connect(config_editor, &ConfigWidget::closeRequest, m_diag_editor, &QDialog::accept);

    m_diag_editor->setWindowTitle(tr("Configuration Globale"));

    m_diag_editor->open();

}
