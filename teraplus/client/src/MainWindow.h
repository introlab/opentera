#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QPropertyAnimation>
#include <QMovie>
#include <QDialog>

#include "editors/UserWidget.h"
#include "ConfigWidget.h"

#include "ComManager.h"
#include "Message.h"

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT


public:

    explicit MainWindow(ComManager* com_manager, QWidget *parent = nullptr);
    ~MainWindow();

signals:
    void logout_request();

private slots:
    void updateCurrentUser();
    void processGenericDataReply(QList<TeraData> datas);

    void com_serverError(QAbstractSocket::SocketError error, QString error_msg);
    void com_networkError(QNetworkReply::NetworkError error, QString error_msg);
    void com_waitingForReply(bool waiting);
    void com_postReplyOK();

    void addMessage(Message::MessageType msg_type, QString msg);
    void addMessage(const Message& msg);
    bool hasWaitingMessage();
    void showNextMessage();

    void editorDialogFinished();
    void dataDisplayRequested(TeraDataTypes data_type, int data_id);
    void dataEditorCancelled();

    void on_btnCloseMessage_clicked();
    void on_btnLogout_clicked();
    void on_btnEditUser_clicked();
    void on_btnConfig_clicked();

private:
    void connectSignals();
    void initUi();
    void showDataEditor(const TeraDataTypes &data_type, const TeraData *data);

    Ui::MainWindow *ui;

    ComManager*         m_comManager;
    QDialog*            m_diag_editor;
    DataEditorWidget*   m_data_editor;
    TeraDataTypes       m_waiting_for_data_type;

    // Message system
    QList<Message>  m_messages;
    Message         m_currentMessage;
    QTimer          m_msgTimer;

    // UI items
    QMovie*         m_loadingIcon;

};

#endif // MAINWINDOW_H
