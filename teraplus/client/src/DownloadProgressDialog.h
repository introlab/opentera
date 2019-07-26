#ifndef DOWNLOADPROGRESSWIDGET_H
#define DOWNLOADPROGRESSWIDGET_H

#include <QDialog>

#include <QTableWidgetItem>
#include "DownloadedFile.h"

namespace Ui {
class DownloadProgressDialog;
}

class DownloadProgressDialog : public QDialog
{
    Q_OBJECT

public:
    explicit DownloadProgressDialog(QWidget *parent = nullptr);
    ~DownloadProgressDialog();

    void updateDownloadedFile(DownloadedFile* file);
    bool downloadFileCompleted(DownloadedFile* file);

private:
    Ui::DownloadProgressDialog *ui;

    QMap<DownloadedFile*, QTableWidgetItem*> m_files;
};

#endif // DOWNLOADPROGRESSWIDGET_H
