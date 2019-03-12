#include "ComManager.h"
#include <sstream>

ComManager::ComManager(QUrl serverUrl, QObject *parent) : QObject(parent)
{
    // Initialize communication objects
    m_webSocket = new QWebSocket(QString(), QWebSocketProtocol::VersionLatest, parent);
    m_connectTimer.setSingleShot(true);
    m_netManager = new QNetworkAccessManager(this);
    m_netManager->setCookieJar(&m_cookieJar);

    // Setup signals and slots
    // Websocket
    connect(m_webSocket, &QWebSocket::connected, this, &ComManager::onSocketConnected);
    connect(m_webSocket, &QWebSocket::disconnected, this, &ComManager::onSocketDisconnected);
    connect(m_webSocket, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(onSocketError(QAbstractSocket::SocketError)));
    connect(m_webSocket, &QWebSocket::sslErrors, this, &ComManager::onSocketSslErrors);
    connect(m_webSocket, &QWebSocket::textMessageReceived, this, &ComManager::onSocketTextMessageReceived);
    connect(m_webSocket, &QWebSocket::binaryMessageReceived, this, &ComManager::onSocketBinaryMessageReceived);

    // Network manager
    connect(m_netManager, &QNetworkAccessManager::authenticationRequired, this, &ComManager::onNetworkAuthenticationRequired);
    connect(m_netManager, &QNetworkAccessManager::encrypted, this, &ComManager::onNetworkEncrypted);
    connect(m_netManager, &QNetworkAccessManager::finished, this, &ComManager::onNetworkFinished);
    connect(m_netManager, &QNetworkAccessManager::networkAccessibleChanged, this, &ComManager::onNetworkAccessibleChanged);
    connect(m_netManager, &QNetworkAccessManager::sslErrors, this, &ComManager::onNetworkSslErrors);

    // Other objects

    connect(&m_connectTimer, &QTimer::timeout, this, &ComManager::onTimerConnectTimeout);

    // Create correct server url
    m_serverUrl.setUrl("https://" + serverUrl.host() + ":" + QString::number(serverUrl.port()));

}

ComManager::~ComManager()
{
    m_webSocket->deleteLater();
}

void ComManager::connectToServer(QString username, QString password)
{
    qDebug() << "ComManager::Connecting to " << m_serverUrl.toString();

    m_username = username;
    m_password = password;

    m_loggingInProgress = true; // Indicate that a login request was sent, but not processed

    QUrl login_url = m_serverUrl;
    login_url.setPath(WEB_LOGIN_PATH);
    m_netManager->get(QNetworkRequest(login_url));

    //m_connectTimer.setInterval(8000);
    //m_connectTimer.start();

}

void ComManager::disconnectFromServer()
{
    QUrl logout_url = m_serverUrl;
    logout_url.setPath(WEB_LOGOUT_PATH);
    m_netManager->get(QNetworkRequest(logout_url));
}

bool ComManager::processNetworkReply(QNetworkReply *reply)
{
    QString reply_path = reply->url().path();
    QString reply_data = reply->readAll();
    qDebug() << reply_path << " ---> " << reply_data;

    bool handled = false;

    if (reply_path == WEB_LOGIN_PATH){
        // Initialize cookies
        m_cookieJar.cookiesForUrl(reply->url());

        handled=handleLoginReply(reply_data);
    }

    if (reply_path == WEB_USERINFO_PATH){
        handled=handleUsersReply(reply_data);
    }

    if (reply_path == WEB_LOGOUT_PATH){
        emit serverDisconnected();
        handled = true;
    }

    return handled;
}

TeraUser& ComManager::getCurrentUser()
{
    return m_currentUser;
}

bool ComManager::handleLoginReply(const QString &reply_data)
{
    QJsonParseError json_error;

    // Process reply
    QJsonDocument login_info = QJsonDocument::fromJson(reply_data.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError)
        return false;

    // Connect websocket
    QString web_socket_url = login_info["websocket_url"].toString();
    m_connectTimer.setInterval(60000);
    m_connectTimer.start();
    m_webSocket->open(QUrl(web_socket_url));

    // Query connected user information
    QString user_uuid = login_info["user_uuid"].toString();
    m_currentUser.setUuid(QUuid(user_uuid));
    QUrl query = m_serverUrl;

    query.setPath(QString(WEB_USERINFO_PATH));
    query.setQuery("user_uuid=" + user_uuid);
    m_netManager->get(QNetworkRequest(query));

    return true;
}

bool ComManager::handleUsersReply(const QString &reply_data)
{
    QJsonParseError json_error;

    // Process reply
    QJsonDocument users = QJsonDocument::fromJson(reply_data.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError)
        return false;

    // Browse each users
    QList<TeraUser> users_data;
    for (QJsonValue user:users.array()){
        TeraUser user_data(user);
        if (m_currentUser.getUuid()==user_data.getUuid()){
            m_currentUser = user_data;
            emit currentUserUpdated();
        }
        users_data.append(user_data);
    }

    // Emit signal
    if (!users_data.isEmpty()){
        emit usersReceived(users_data);
    }


    return true;
}


//////////////////////////////////////////////////////////////////////
void ComManager::onSocketError(QAbstractSocket::SocketError error)
{
    qDebug() << "ComManager::Socket error - " << error;
    emit serverError(error, m_webSocket->errorString());
}

void ComManager::onSocketConnected()
{
    m_connectTimer.stop();
    emit loginResult(true); // Logged in
}

void ComManager::onSocketDisconnected()
{
    m_connectTimer.stop();
    qDebug() << "ComManager::Disconnected from " << m_serverUrl.toString();
    emit serverDisconnected();
}

void ComManager::onSocketSslErrors(const QList<QSslError> &errors)
{
    Q_UNUSED(errors);

    // WARNING: Never ignore SSL errors in production code.
    // The proper way to handle self-signed certificates is to add a custom root
    // to the CA store.
    qDebug() << "ComManager::SSlErrors " << errors;
    m_webSocket->ignoreSslErrors();
}

void ComManager::onSocketTextMessageReceived(const QString &message)
{
    LOG_DEBUG(message, "ComManager::onSocketTextMessageReceived");
}

void ComManager::onSocketBinaryMessageReceived(const QByteArray &message)
{
    Q_UNUSED(message)
}

/////////////////////////////////////////////////////////////////////////////////////
void ComManager::onNetworkAuthenticationRequired(QNetworkReply *reply, QAuthenticator *authenticator)
{
    Q_UNUSED(reply);
    if (m_loggingInProgress){
        LOG_DEBUG("Sending authentication request...", "ComManager::onNetworkAuthenticationRequired");
        authenticator->setUser(m_username);
        authenticator->setPassword(m_password);
        m_loggingInProgress = false; // Not logging anymore - we sent the credentials
    }else{
        LOG_DEBUG("Authentication error", "ComManager::onNetworkAuthenticationRequired");
        emit loginResult(false);
    }
}

void ComManager::onNetworkEncrypted(QNetworkReply *reply)
{
    Q_UNUSED(reply);
    qDebug() << "ComManager::onNetworkEncrypted";
}

void ComManager::onNetworkFinished(QNetworkReply *reply)
{
    if (reply->error() == QNetworkReply::NoError)
    {
        if (!processNetworkReply(reply)){
            LOG_WARNING("Unhandled reply - " + reply->url().path(), "ComManager::onNetworkFinished");
        }
    }
    else {
        qDebug() << "ComManager::onNetworkFinished - Reply error: " << reply->error();
        emit networkError(reply->error(), reply->errorString());
    }
    reply->deleteLater();
}

void ComManager::onNetworkAccessibleChanged(QNetworkAccessManager::NetworkAccessibility accessible)
{
    Q_UNUSED(accessible)

    qDebug() << "ComManager::onNetworkAccessibleChanged";
    //TODO: Emit signal
}

void ComManager::onNetworkSslErrors(QNetworkReply *reply, const QList<QSslError> &errors)
{
    Q_UNUSED(reply);
    Q_UNUSED(errors);
    LOG_WARNING("Ignoring SSL errors, this is unsafe", "ComManager::onNetworkSslErrors");
    reply->ignoreSslErrors();
    for(QSslError error : errors){
        LOG_WARNING("Ignored: " + error.errorString(), "ComManager::onNetworkSslErrors");
    }
}

void ComManager::onTimerConnectTimeout()
{
    // Connection timeout
    if (m_webSocket){
        qDebug() << "ComManager::onTimerConnectTimeout()";
        m_webSocket->abort();
        emit serverError(QAbstractSocket::SocketTimeoutError, tr("Le serveur ne répond pas."));
    }

}
