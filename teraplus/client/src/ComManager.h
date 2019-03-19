#ifndef COMMANAGER_H
#define COMMANAGER_H

#include <QObject>
#include <QWebSocket>
#include <QAbstractSocket>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QAuthenticator>
#include <QNetworkProxy>
#include <QSslPreSharedKeyAuthenticator>
#include <QNetworkCookieJar>
#include <QNetworkCookie>
#include <QWebSocket>

#include <QJsonDocument>
#include <QJsonParseError>
#include <QJsonArray>
#include <QJsonValue>

#include <QUrl>
#include <QTimer>
#include <QUuid>

#include "Logger.h"
#include "webapi.h"

#include "TeraUser.h"


class ComManager : public QObject
{
    Q_OBJECT
public:
    explicit ComManager(QUrl serverUrl, QObject *parent = nullptr);
    ~ComManager();

    void connectToServer(QString username, QString password);
    void disconnectFromServer();

    bool processNetworkReply(QNetworkReply* reply);
    void doQuery(const QString &path, const QString &query_args = QString());

    TeraUser &getCurrentUser();

protected:
    bool handleLoginReply(const QString& reply_data);
    bool handleUsersReply(const QString& reply_data);


    QUrl                    m_serverUrl;
    QNetworkAccessManager*  m_netManager;
    QNetworkCookieJar       m_cookieJar;
    QWebSocket*             m_webSocket;

    bool                    m_loggingInProgress;

    QString                 m_username;
    QString                 m_password;

    QTimer                  m_connectTimer;

    TeraUser                m_currentUser;

signals:
    void serverDisconnected();
    void serverError(QAbstractSocket::SocketError, QString);
    void networkError(QNetworkReply::NetworkError, QString);
    void waitingForReply(bool waiting);

    void loginResult(bool logged_in);

    void currentUserUpdated();

    void usersReceived(QList<TeraUser> user_list);
    void profileDefReceived(QString profile);

public slots:

private slots:
    // Websockets
    void onSocketConnected();
    void onSocketDisconnected();
    void onSocketError(QAbstractSocket::SocketError error);
    void onSocketSslErrors(const QList<QSslError> &errors);
    void onSocketTextMessageReceived(const QString &message);
    void onSocketBinaryMessageReceived(const QByteArray &message);

    // Network
    void onNetworkAuthenticationRequired(QNetworkReply *reply, QAuthenticator *authenticator);
    void onNetworkEncrypted(QNetworkReply *reply);
    void onNetworkFinished(QNetworkReply *reply);
    void onNetworkAccessibleChanged(QNetworkAccessManager::NetworkAccessibility accessible);
    void onNetworkSslErrors(QNetworkReply *reply, const QList<QSslError> &errors);

    void onTimerConnectTimeout();
};

#endif // COMMANAGER_H
