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
    bool hasWaitingMessage();
    void showNextMessage();

    void editorDialogFinished();

    void on_btnCloseMessage_clicked();
    void on_btnLogout_clicked();
    void on_btnEditUser_clicked();
    void on_btnConfig_clicked();

    void newItemRequested();

private:
    void connectSignals();
    void initUi();

    QAction* addNewItemAction(const TeraDataTypes &data_type, const QString& label);


    Ui::MainWindow *ui;

    ComManager*     m_comManager;
    QDialog*        m_diag_editor;

    // Message system
    QList<Message>  m_messages;
    Message         m_currentMessage;
    QTimer          m_msgTimer;

    // UI items
    QMovie*         m_loadingIcon;
    QMenu*          m_newItemMenu;
    QList<QAction*> m_newItemActions;

};

#endif // MAINWINDOW_H
