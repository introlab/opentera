#ifndef CLIENTAPP_H
#define CLIENTAPP_H

#include <QObject>
#include <QApplication>
#include <QFile>
#include <QAbstractSocket> // For error codes
#include <QUuid>

#include "MainWindow.h"
#include "LoginDialog.h"

#include "ComManager.h"
#include "ConfigManagerClient.h"

class ClientApp : public QApplication
{
    Q_OBJECT
public:
    ClientApp(int &argc, char** argv);
    ~ClientApp();

    ComManager *getComManager();

protected:
    void loadConfig();
    void connectSignals();
    void showLogin();
    void showMainWindow();

    ConfigManagerClient m_config;
    LoginDialog*        m_loginDiag;
    MainWindow*         m_mainWindow;

    ComManager*         m_comMan;


private slots:
    void loginRequested(QString username, QString password, QString server_name);
    void on_loginResult(bool logged);
    void on_currentUserUpdated();

    void on_serverDisconnected();
    void on_serverError(QAbstractSocket::SocketError error, QString error_str);
    void on_networkError(QNetworkReply::NetworkError error, QString error_str);
};

#endif // CLIENTAPP_H
