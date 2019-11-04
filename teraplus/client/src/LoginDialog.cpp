#include "LoginDialog.h"
#include "ui_LoginDialog.h"

LoginDialog::LoginDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::LoginDialog)
{
    ui->setupUi(this);
    //setAttribute(Qt::WA_StyledBackground);
    //setStyleSheet("QDialog{background-image: url(://TeRA_Background.png); }");

    // Setup properties
    setSizeGripEnabled(false);
    setFixedWidth(450);
    setWindowFlags(Qt::FramelessWindowHint | Qt::Dialog);

    // Setup loading icon animation
    m_animatedIcon = new QMovie("://status/loading.gif");
    ui->lblLoadingIcon->setMovie(m_animatedIcon);
    m_animatedIcon->start();

    // Hide messages
    ui->frameMessage->hide();
    ui->lblWarningIcon->hide();

    ui->txtUsername->setFocus();
}

LoginDialog::~LoginDialog()
{
    m_animatedIcon->deleteLater();
    delete ui;
}

void LoginDialog::setServerNames(QStringList servers)
{
    ui->cmbServers->clear();
    foreach(QString server, servers){
        ui->cmbServers->addItem(server);
    }
    if(servers.count()>0)
        ui->cmbServers->setCurrentIndex(0);
}

void LoginDialog::showServers(bool show)
{
    ui->lblServer->setVisible(show);
    ui->cmbServers->setVisible(show);
}

void LoginDialog::setStatusMessage(QString message, bool error)
{
    if (message.isEmpty()){
        ui->frameMessage->hide();
    }else{
        if (error)
            ui->lblMessage->setStyleSheet("color:red;");
        else {
            ui->lblMessage->setStyleSheet("color:yellow;");
        }
        ui->lblMessage->setText(message);
        ui->lblWarningIcon->setVisible(error);
        ui->lblLoadingIcon->setVisible(!error);
        ui->frameMessage->show();
    }
    ui->frameLogin->setEnabled(error);
    ui->btnConnect->setEnabled(error);
}

void LoginDialog::on_btnQuit_clicked()
{
    QApplication::quit();
}

void LoginDialog::on_btnConnect_clicked()
{
    if (ui->txtUsername->text().isEmpty()){
        setStatusMessage(tr("Code utilisateur invalide"),true);
        return;
    }

    if (ui->txtPassword->text().isEmpty()){
        setStatusMessage(tr("Mot de passe invalide"), true);
        return;
    }

    setStatusMessage(tr("Connexion en cours..."));

    emit loginRequest(ui->txtUsername->text(), ui->txtPassword->text(), ui->cmbServers->currentText());


}
