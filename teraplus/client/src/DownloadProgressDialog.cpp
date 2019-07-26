#include "DownloadProgressDialog.h"
#include "ui_DownloadProgressDialog.h"

#include <QProgressBar>

DownloadProgressDialog::DownloadProgressDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::DownloadProgressDialog)
{
    ui->setupUi(this);
    setWindowFlags(Qt::SplashScreen);
}

DownloadProgressDialog::~DownloadProgressDialog()
{
    delete ui;
}

void DownloadProgressDialog::updateDownloadedFile(DownloadedFile *file)
{
    QTableWidgetItem* item;
    QProgressBar* progress;
    if (!m_files.contains(file)){
        // Must create a new file in the list
        ui->tableDownloads->setRowCount(ui->tableDownloads->rowCount()+1);

        item = new QTableWidgetItem(file->getFullFilename());
        ui->tableDownloads->setItem(ui->tableDownloads->rowCount()-1,1,item);
        m_files[file] = item;

        progress = new QProgressBar();
        progress->setMinimum(0);
        progress->setAlignment(Qt::AlignHCenter | Qt::AlignVCenter);
        ui->tableDownloads->setCellWidget(ui->tableDownloads->rowCount()-1,0,progress);
    }else{
        item = m_files[file];
        progress = dynamic_cast<QProgressBar*>(ui->tableDownloads->cellWidget(item->row(),0));
    }

    // Update values
    if (progress){
        progress->setMaximum(static_cast<int>(file->totalBytes()));
        progress->setValue(static_cast<int>(file->currentBytes()));
    }

}

bool DownloadProgressDialog::downloadFileCompleted(DownloadedFile *file)
{
    updateDownloadedFile(file);

    // Remove file from list
    m_files.remove(file);

    return m_files.isEmpty(); // No more files to display?
}
