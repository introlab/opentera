#ifndef BASE_DIALOG_H_
#define BASE_DIALOG_H_

#include <QDialog>
#include <QVBoxLayout>
#include "ui_BaseDialog.h"

class BaseDialog : public QDialog
{
    Q_OBJECT

public:
    BaseDialog(QWidget *parent = nullptr);

    void setCentralWidget(QWidget *widget);

    //QWidget* centralWidget();

protected:

    Ui::BaseDialog m_ui;
    QVBoxLayout *m_centralWidgetLayout;

};

#endif

