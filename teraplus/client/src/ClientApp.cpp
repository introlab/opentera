#include "ClientApp.h"
#include <QDebug>
#include <QFileInfo>
#include <QDir>

ClientApp::ClientApp(int &argc, char **argv)
 :   QApplication(argc, argv)
{
    m_comMan = nullptr;
    m_loginDiag = nullptr;
    m_mainWindow = nullptr;

    setApplicationName(QString("TeraClient v") + QString(TERAPLUS_VERSION));
    qDebug() << "Starting App " << applicationName();

    // Load config
    loadConfig();

    // Connect signals
    connectSignals();

    // Show login dialog
    showLogin();
}

ClientApp::~ClientApp()
{
    if (m_loginDiag)
        delete m_loginDiag;

}

ComManager *ClientApp::getComManager()
{
    return m_comMan;
}

void ClientApp::loadConfig()
{
    QString configFile = applicationDirPath() + "/config/client/TeraClientConfig.txt";
    qDebug() << "Loading config file: " << configFile;

    // Check if config file exists and, if not, copy from QRC
    if (!QFile::exists(configFile)){
        qDebug() << "ClientApp : No Config File - Creating new one.";
        // Create folder if not exists
        QFileInfo config_file_info(configFile);
        QDir config_folder;
        config_folder.mkpath(config_file_info.path());
        QFile::copy("://defaults/TeraClientConfig.txt", configFile);
    }

    m_config.setFilename(configFile);

    if (!m_config.loadConfig()){
        if (!m_config.hasParseError()){ // Missing file
            qDebug() << "Can't load file: " << configFile;
        }else{
            qDebug() << "Parse error: " << m_config.getLastError().errorString() << " at character " << m_config.getLastError().offset;
        }
    }
}

void ClientApp::connectSignals()
{

}

void ClientApp::showLogin()
{
    if (m_loginDiag == nullptr){
        m_loginDiag = new LoginDialog();
        connect(m_loginDiag, &LoginDialog::loginRequest, this, &ClientApp::loginRequested);

        // Set server names
        m_loginDiag->setServerNames(m_config.getServerNames());

        // Show servers list... or not!
        m_loginDiag->showServers(m_config.showServers());
    }

    // Delete main window, if present
    if (m_mainWindow){
        m_mainWindow->deleteLater();
        m_mainWindow = nullptr;
    }
    m_loginDiag->show();
}

void ClientApp::showMainWindow()
{
    if (m_mainWindow != nullptr){
        m_mainWindow->deleteLater();
    }
    m_mainWindow = new MainWindow(m_comMan);

    // Delete login window, if present
    if (m_loginDiag){
        m_loginDiag->deleteLater();
        m_loginDiag = nullptr;
    }

    // Connect signals
    connect(m_mainWindow, &MainWindow::logout_request, this, &ClientApp::logoutRequested);

    m_mainWindow->showMaximized();
}

void ClientApp::loginRequested(QString username, QString password, QString server_name)
{
    // Find server url for that server
    QUrl server = m_config.getServerUrl(server_name);

    // Create ComManager for that server
    if (m_comMan){
        m_comMan->deleteLater();
    }
    m_comMan = new ComManager(server);

    // Connect signals
    connect(m_comMan, &ComManager::serverError, this, &ClientApp::on_serverError);
    connect(m_comMan, &ComManager::serverDisconnected, this, &ClientApp::on_serverDisconnected);
    connect(m_comMan, &ComManager::loginResult, this, &ClientApp::on_loginResult);
    connect(m_comMan, &ComManager::networkError, this, &ClientApp::on_networkError);

    // Connect to server
    m_comMan->connectToServer(username, password);

}

void ClientApp::logoutRequested()
{
    m_comMan->disconnectFromServer();
}

void ClientApp::on_loginResult(bool logged)
{
    if (!logged){
        m_loginDiag->setStatusMessage(tr("Utilisateur ou mot de passe invalide."),true);
    }else{
        m_loginDiag->setStatusMessage(tr("Bienvenue!"));
        showMainWindow();
    }
}

void ClientApp::on_serverDisconnected()
{
    showLogin();
}

void ClientApp::on_serverError(QAbstractSocket::SocketError error, QString error_str)
{
    if (m_loginDiag){
        if (error == QAbstractSocket::ConnectionRefusedError)
            error_str = tr("La connexion a été refusée par le serveur.");
        m_loginDiag->setStatusMessage(error_str, true);
    }

    // TODO: Manage error in main UI
}

void ClientApp::on_networkError(QNetworkReply::NetworkError error, QString error_str)
{
    if (m_loginDiag){
        if (error == QNetworkReply::ConnectionRefusedError)
            error_str = tr("La connexion a été refusée par le serveur.");
        if (error == QNetworkReply::AuthenticationRequiredError){
            on_loginResult(false);
            return;
        }
        m_loginDiag->setStatusMessage(error_str, true);
    }
    // TODO: Manage error in main UI
}
