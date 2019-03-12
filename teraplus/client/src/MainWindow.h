#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "data/TeraUser.h"
#include "ComManager.h"

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

    void on_btnLogout_clicked();

private:
    void connectSignals();

    Ui::MainWindow *ui;

    ComManager* m_comManager;

};

#endif // MAINWINDOW_H
