#include "MainWindow.h"

#include "ui_MainWindow.h"

MainWindow::MainWindow(ComManager *com_manager, QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    m_comManager = com_manager;

    // Initial UI state
    initUi();

    // Connect signals
    connectSignals();
}

MainWindow::~MainWindow()
{
    delete ui;
    delete m_loadingIcon;
}

void MainWindow::connectSignals()
{
    connect(m_comManager, &ComManager::currentUserUpdated, this, &MainWindow::updateCurrentUser);
    connect(m_comManager, &ComManager::networkError, this, &MainWindow::com_networkError);
    connect(m_comManager, &ComManager::serverError, this, &MainWindow::com_serverError);
    connect(m_comManager, &ComManager::waitingForReply, this, &MainWindow::com_waitingForReply);
    connect(&m_msgTimer, &QTimer::timeout, this, &MainWindow::showNextMessage);
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

}

void MainWindow::showNextMessage()
{
    m_loadingIcon->stop();
    ui->frameMessages->hide();
    m_msgTimer.stop();
    if (m_messages.isEmpty()){
        return;
    }

    Message msg = m_messages.takeFirst();

    QString background_color = "rgba(128,128,128,50%)";
    QString icon_path = "";

    switch(msg.getMessageType()){
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
    }
    ui->frameMessages->setStyleSheet("background-color: " + background_color + ";");
    ui->lblMessage->setText(msg.getMessageText());
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

void MainWindow::updateCurrentUser()
{
    ui->lblUser->setText(m_comManager->getCurrentUser().getName());
}

void MainWindow::com_serverError(QAbstractSocket::SocketError error, QString error_msg)
{
    Q_UNUSED(error)
    addMessage(Message::MESSAGE_ERROR, error_msg);
}

void MainWindow::com_networkError(QNetworkReply::NetworkError error, QString error_msg)
{
    Q_UNUSED(error)
    addMessage(Message::MESSAGE_ERROR, error_msg);
}

void MainWindow::com_waitingForReply(bool waiting)
{
    if (waiting){
        addMessage(Message::MESSAGE_WORKING, "");
    }else{
        showNextMessage();
    }
    ui->btnEditUser->setEnabled(!waiting);
    ui->btnConfig->setEnabled(!waiting);
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

void MainWindow::on_btnCloseMessage_clicked()
{
    showNextMessage();
}

void MainWindow::on_btnEditUser_clicked()
{
    QDialog diag(this);
    UserWidget* user_editor = new UserWidget(m_comManager, m_comManager->getCurrentUser(), &diag);
    user_editor->setLimited(true);
    connect(user_editor, &UserWidget::closeRequest, &diag, &QDialog::close);

    diag.setWindowTitle(tr("Votre compte"));

    diag.exec();
}
