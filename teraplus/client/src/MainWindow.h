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

    void com_serverError(QAbstractSocket::SocketError error, QString error_msg);
    void com_networkError(QNetworkReply::NetworkError error, QString error_msg);
    void com_waitingForReply(bool waiting);
    void com_postReplyOK();

    void addMessage(Message::MessageType msg_type, QString msg);
    void addMessage(const Message& msg);
    void showNextMessage();

    void editorDialogFinished();

    void on_btnCloseMessage_clicked();
    void on_btnLogout_clicked();

    void on_btnEditUser_clicked();

    void on_btnConfig_clicked();

private:
    void connectSignals();
    void initUi();


    Ui::MainWindow *ui;

    ComManager*     m_comManager;
    QDialog*        m_diag_editor;

    // Message system
    QList<Message>  m_messages;
    QMovie*         m_loadingIcon;
    QTimer          m_msgTimer;

};

#endif // MAINWINDOW_H
