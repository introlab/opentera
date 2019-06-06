#include "ComManager.h"
#include <sstream>

ComManager::ComManager(QUrl serverUrl, QObject *parent) :
    QObject(parent),
    m_currentUser(TERADATA_USER)
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

    doQuery(QString(WEB_LOGIN_PATH));

}

void ComManager::disconnectFromServer()
{
    doQuery(QString(WEB_LOGOUT_PATH));
}

bool ComManager::processNetworkReply(QNetworkReply *reply)
{
    QString reply_path = reply->url().path();
    QString reply_data = reply->readAll();
    QUrlQuery reply_query = QUrlQuery(reply->url().query());
    //qDebug() << reply_path << " ---> " << reply_data << ": " << reply_query;

    bool handled = false;

    if (reply->operation()==QNetworkAccessManager::GetOperation){
        if (reply_path == WEB_LOGIN_PATH){
            // Initialize cookies
            m_cookieJar.cookiesForUrl(reply->url());

            handled=handleLoginReply(reply_data);
        }

        if (reply_path == WEB_LOGOUT_PATH){
            emit serverDisconnected();
            handled = true;
        }

        if (reply_path == WEB_FORMS_PATH){
            handled = handleFormReply(reply_query, reply_data);
            if (handled) emit queryResultsOK(reply_path, reply_query);
        }

        if (!handled){
            // General case
            handled=handleDataReply(reply_path, reply_data, reply_query);
            if (handled) emit queryResultsOK(reply_path, reply_query);
        }
    }

    if (reply->operation()==QNetworkAccessManager::PostOperation){
        handled=handleDataReply(reply_path, reply_data, reply_query);
        if (handled) emit postResultsOK(reply_path);
    }

    if (reply->operation()==QNetworkAccessManager::DeleteOperation){
        // Extract id from url
        int id = 0;
        if (reply_query.hasQueryItem("id")){
            id = reply_query.queryItemValue("id").toInt();
        }
        emit deleteResultsOK(reply_path, id);
        handled=true;
    }

    return handled;
}

void ComManager::doQuery(const QString &path, const QUrlQuery &query_args)
{
    QUrl query = m_serverUrl;

    query.setPath(path);
    if (!query_args.isEmpty()){
        query.setQuery(query_args);
    }
    m_netManager->get(QNetworkRequest(query));
    emit waitingForReply(true);

    LOG_DEBUG("GET: " + path + ", with " + query_args.toString(), "ComManager::doQuery");
}

void ComManager::doPost(const QString &path, const QString &post_data)
{
    QUrl query = m_serverUrl;

    query.setPath(path);
    QNetworkRequest request(query);
    request.setRawHeader("Content-Type", "application/json");
    m_netManager->post(request, post_data.toUtf8());
    emit waitingForReply(true);

    LOG_DEBUG("POST: " + path + ", with " + post_data, "ComManager::doPost");
}

void ComManager::doDelete(const QString &path, const int &id)
{
    QUrl query = m_serverUrl;

    query.setPath(path);
    query.setQuery("id=" + QString::number(id));
    QNetworkRequest request(query);
    m_netManager->deleteResource(request);
    emit waitingForReply(true);
    LOG_DEBUG("DELETE: " + path + ", with ID=" + QString::number(id), "ComManager::doDelete");
}

void ComManager::doUpdateCurrentUser()
{
    doQuery(QString(WEB_USERINFO_PATH), QUrlQuery("user_uuid=" + m_currentUser.getFieldValue("user_uuid").toUuid().toString(QUuid::WithoutBraces)));
}

TeraData &ComManager::getCurrentUser()
{
    return m_currentUser;
}

QString ComManager::getCurrentUserSiteRole(int site_id)
{
    QString rval = "";

    if (m_currentUser.hasFieldName("sites")){
        QVariantList sites_list = m_currentUser.getFieldValue("sites").toList();
        for (int i=0; i<sites_list.count(); i++){
            QVariantMap site_info = sites_list.at(i).toMap();
            if (site_info.contains("id_site")){
                if (site_info["id_site"].toInt() == site_id){
                    if (site_info.contains("site_role")){
                        rval = site_info["site_role"].toString();
                        break;
                    }
                }
            }
        }
    }

    return rval;
}

QString ComManager::getCurrentUserProjectRole(int project_id)
{
    QString rval = "";

    if (m_currentUser.hasFieldName("projects")){
        QVariantList proj_list = m_currentUser.getFieldValue("projects").toList();
        for (int i=0; i<proj_list.count(); i++){
            QVariantMap proj_info = proj_list.at(i).toMap();
            if (proj_info.contains("id_project")){
                if (proj_info["id_project"].toInt() == project_id){
                    if (proj_info.contains("project_role")){
                        rval = proj_info["project_role"].toString();
                        break;
                    }
                }
            }
        }
    }

    return rval;
}

bool ComManager::isCurrentUserSuperAdmin()
{
    bool rval = false;
    if (m_currentUser.hasFieldName("user_superadmin")){
        rval = m_currentUser.getFieldValue("user_superadmin").toBool();
    }
    return rval;
}

ComManager::signal_ptr ComManager::getSignalFunctionForDataType(const TeraDataTypes &data_type)
{
    switch(data_type){
    case TERADATA_NONE:
        LOG_ERROR("Unknown object - no signal associated.", "ComManager::getSignalFunctionForDataType");
        return nullptr;
    case TERADATA_USER:
        return &ComManager::usersReceived;
    case TERADATA_SITE:
        return &ComManager::sitesReceived;
    case TERADATA_KIT:
        return &ComManager::kitsReceived;
    case TERADATA_SESSIONTYPE:
        return &ComManager::sessionTypesReceived;
    case TERADATA_TESTDEF:
        return &ComManager::testDefsReceived;
    case TERADATA_PROJECT:
        return &ComManager::projectsReceived;
    case TERADATA_DEVICE:
        return &ComManager::devicesReceived;
    case TERADATA_GROUP:
        return &ComManager::groupsReceived;
    case TERADATA_PARTICIPANT:
        return &ComManager::participantsReceived;
    case TERADATA_SITEACCESS:
        return &ComManager::siteAccessReceived;
    case TERADATA_KITDEVICE:
        return &ComManager::kitDevicesReceived;
    case TERADATA_PROJECTACCESS:
        return &ComManager::projectAccessReceived;
    case TERADATA_SESSION:
        return &ComManager::sessionsReceived;
    }

    return nullptr;
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
    m_connectTimer.setInterval(60000); //TODO: Reduce this delay - was set that high because of the time required to connect in MAC OS
    m_connectTimer.start();
    m_webSocket->open(QUrl(web_socket_url));

    // Query connected user information
    QString user_uuid = login_info["user_uuid"].toString();
    m_currentUser.setFieldValue("user_uuid", QUuid(user_uuid));
    doUpdateCurrentUser();

    return true;
}

bool ComManager::handleDataReply(const QString& reply_path, const QString &reply_data, const QUrlQuery &reply_query)
{
    QJsonParseError json_error;

    // Process reply
    QJsonDocument data_list = QJsonDocument::fromJson(reply_data.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError)
        return false;

    // Browse each items received
    QList<TeraData> items;
    TeraDataTypes items_type = TeraData::getDataTypeFromPath(reply_path);
    for (QJsonValue data:data_list.array()){
        TeraData item_data(items_type, data);

        // Check if the currently connected user was updated and not requesting a list (limited information)
        if (items_type == TERADATA_USER){
            if (m_currentUser.getFieldValue("user_uuid").toUuid() == item_data.getFieldValue("user_uuid").toUuid() &&
                    !reply_query.hasQueryItem(WEB_QUERY_LIST)){
                m_currentUser = item_data;
                emit currentUserUpdated();
            }
        }
        items.append(item_data);
    }

    // Emit signal
    switch (items_type) {
    case TERADATA_NONE:
        LOG_ERROR("Unknown object - don't know what to do with it.", "ComManager::handleDataReply");
        break;
    case TERADATA_USER:
        emit usersReceived(items);
        break;
    case TERADATA_SITE:
        emit sitesReceived(items);
        break;
    case TERADATA_KIT:
        emit kitsReceived(items);
        break;
    case TERADATA_SESSIONTYPE:
        emit sessionTypesReceived(items);
        break;
    case TERADATA_TESTDEF:
        emit testDefsReceived(items);
        break;
    case TERADATA_PROJECT:
        emit projectsReceived(items);
        break;
    case TERADATA_DEVICE:
        emit devicesReceived(items);
        break;
    case TERADATA_PARTICIPANT:
        emit participantsReceived(items);
        break;
    case TERADATA_GROUP:
        emit groupsReceived(items);
        break;
    case TERADATA_SITEACCESS:
        emit siteAccessReceived(items);
        break;
    case TERADATA_KITDEVICE:
        emit kitDevicesReceived(items);
        break;
    case TERADATA_PROJECTACCESS:
        emit projectAccessReceived(items);
        break;
    case TERADATA_SESSION:
        emit sessionsReceived(items);
        break;
/*    default:
        emit getSignalFunctionForDataType(items_type);*/

    }

    // Always emit generic signal
    emit dataReceived(items);

    return true;
}

bool ComManager::handleFormReply(const QUrlQuery &reply_query, const QString &reply_data)
{
    emit formReceived(reply_query.toString(), reply_data);
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
    emit waitingForReply(false);

    if (reply->error() == QNetworkReply::NoError)
    {
        if (!processNetworkReply(reply)){
            LOG_WARNING("Unhandled reply - " + reply->url().path(), "ComManager::onNetworkFinished");
        }
    }
    else {
        QString reply_msg = QString(reply->readAll()).replace("""", "");
        if (reply_msg.isEmpty() || reply_msg.startsWith("""""")){
            //reply_msg = tr("Erreur non-détaillée.");
            reply_msg = reply->errorString();
        }
        qDebug() << "ComManager::onNetworkFinished - Reply error: " << reply->error() << ", Reply message: " << reply_msg;
        /*if (reply_msg.isEmpty())
            reply_msg = reply->errorString();*/
        emit networkError(reply->error(), reply_msg);
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
