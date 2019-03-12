#include "MainWindow.h"
#include "ui_MainWindow.h"

MainWindow::MainWindow(ComManager *com_manager, QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    m_comManager = com_manager;

    // Initial UI state
    // Disable top docker title
    ui->dockerTop->setTitleBarWidget(new QWidget());

    // Connect signals
    connectSignals();
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::connectSignals()
{
    connect(m_comManager, &ComManager::currentUserUpdated, this, &MainWindow::updateCurrentUser);
}

void MainWindow::updateCurrentUser()
{
    ui->lblUser->setText(m_comManager->getCurrentUser().getName());
}

void MainWindow::on_btnLogout_clicked()
{
    emit logout_request();
}
