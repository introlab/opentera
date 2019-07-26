#include "DownloadedFile.h"
#include <QDebug>

DownloadedFile::DownloadedFile(QObject *parent) : QObject(parent)
{
    m_reply = nullptr;
    m_filename = "";
    m_savepath = "";
}

DownloadedFile::DownloadedFile(QNetworkReply *reply, const QString &save_path, QObject *parent)
    : QObject(parent)
{
    setNetworkReply(reply);
    m_savepath = save_path;
    m_filename = "";

}

DownloadedFile::DownloadedFile(const DownloadedFile &copy, QObject *parent) : QObject(parent)
{
    *this = copy;
}

DownloadedFile &DownloadedFile::operator =(const DownloadedFile &other)
{
    //m_file = other.m_file;
    m_filename = other.m_filename;
    setNetworkReply(other.m_reply);
    m_savepath = other.m_savepath;
    m_totalBytes = other.m_totalBytes;
    m_currentBytes = other.m_currentBytes;

    return *this;
}

void DownloadedFile::setNetworkReply(QNetworkReply *reply)
{
    m_reply = reply;
    connect(m_reply, &QNetworkReply::readyRead, this, &DownloadedFile::onDownloadDataReceived);
    connect(m_reply, &QNetworkReply::downloadProgress, this, &DownloadedFile::onDownloadProgress);
    connect(m_reply, &QNetworkReply::finished, this, &DownloadedFile::onDownloadCompleted);
}

QString DownloadedFile::getFullFilename()
{
    return m_savepath + "/" + m_filename;
}

qint64 DownloadedFile::totalBytes()
{
    return m_totalBytes;
}

qint64 DownloadedFile::currentBytes()
{
    return m_currentBytes;
}

void DownloadedFile::abortDownload()
{
    qDebug() << "Aborting download...";
    m_reply->abort();
    if (m_file.isOpen()){
        m_file.close();
        QDir dir;
        if (dir.exists(getFullFilename()))
            dir.remove(getFullFilename());
    }
}

void DownloadedFile::onDownloadDataReceived()
{
    // Check if we have a file open for writing
    if (!m_file.isOpen()){
        // Get filename from reply
        QString header_info = m_reply->header(QNetworkRequest::ContentDispositionHeader).toString();
        QStringList header_info_parts = header_info.split(";");
        if (header_info_parts.count()>0){
            if (header_info_parts.first() != "attachment"){
                m_lastError = tr("Impossible de télécharger un objet qui n'est pas de type 'attachment'.");
                qDebug() << m_lastError;
                abortDownload();
                return;
            }
            for (QString info: header_info_parts){
                if (info.trimmed().startsWith("filename=")){
                    QStringList file_parts = info.split("=");
                    if (file_parts.count() == 2)
                        m_filename = file_parts.last();
                    break;
                }
            }
            if (m_filename.isEmpty()){
                m_lastError = tr("Impossible de déterminer le nom du fichier à télécharger.");
                qDebug() << m_lastError;
                abortDownload();
                return;
            }
        }else{
            m_lastError = tr("Mauvaise en-tête pour le téléchargement du fichier.");
            qDebug() << m_lastError;
            abortDownload();
            return;
        }

        // Open the file for writing
        m_file.setFileName(getFullFilename());
        if (!m_file.open(QIODevice::WriteOnly)){
            m_lastError = tr("Impossible d'ouvrir le fichier '") + getFullFilename() + "': " + m_file.errorString();
            qDebug() << m_lastError;
            abortDownload();
            return;
        }
        qDebug() << "Saving to: " << getFullFilename();
    }
    QByteArray data = m_reply->readAll();
    m_file.write(data);

}

void DownloadedFile::onDownloadProgress(qint64 bytesReceived, qint64 bytesTotal)
{
    m_totalBytes = bytesTotal;
    m_currentBytes = bytesReceived;
    //qDebug() << "Received " << bytesReceived << " bytes on " << bytesTotal << " bytes for file " << m_reply->header(QNetworkRequest::ContentDispositionHeader).toString();
    emit downloadProgress(this);
}

void DownloadedFile::onDownloadCompleted()
{
    m_file.close();
    qDebug() << "Download completed.";
    emit downloadComplete(this);
}
