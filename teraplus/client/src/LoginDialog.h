#ifndef LOGINDIALOG_H
#define LOGINDIALOG_H

#include <QDialog>
#include <QMovie>

namespace Ui {
class LoginDialog;
}

class LoginDialog : public QDialog
{
    Q_OBJECT

public:
    explicit LoginDialog(QWidget *parent = nullptr);
    ~LoginDialog();

    void setServerNames(QStringList servers);
    void showServers(bool show);

    void setStatusMessage(QString message, bool error=false);

private:

private slots:
    void on_btnQuit_clicked();
    void on_btnConnect_clicked();   

signals:
    void loginRequest(QString username, QString password, QString server_name);

private:
    Ui::LoginDialog *ui;

    QMovie*     m_animatedIcon;
};

#endif // LOGINDIALOG_H
