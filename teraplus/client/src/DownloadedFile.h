#ifndef DOWNLOADEDFILE_H
#define DOWNLOADEDFILE_H

#include <QObject>
#include <QNetworkReply>
#include <QFile>
#include <QDir>

class DownloadedFile : public QObject
{
    Q_OBJECT
public:
    explicit DownloadedFile(QObject *parent = nullptr);
    DownloadedFile(QNetworkReply* reply, const QString& save_path, QObject *parent = nullptr);
    DownloadedFile(const DownloadedFile& copy, QObject *parent=nullptr);

    DownloadedFile &operator = (const DownloadedFile& other);

    void setNetworkReply(QNetworkReply* reply);
    QString getFullFilename();

    qint64 totalBytes();
    qint64 currentBytes();

    void abortDownload();

private:
    QString         m_savepath;
    QString         m_filename;
    QFile           m_file;
    QNetworkReply*  m_reply;
    qint64          m_totalBytes;
    qint64          m_currentBytes;
    QString         m_lastError;

signals:
    void downloadProgress(DownloadedFile* downloaded_file);
    void downloadComplete(DownloadedFile* downloaded_file);

private slots:
    void onDownloadDataReceived();
    void onDownloadProgress(qint64 bytesReceived, qint64 bytesTotal);
    void onDownloadCompleted();

};

#endif // DOWNLOADEDFILE_H
