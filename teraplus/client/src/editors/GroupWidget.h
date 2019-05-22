#ifndef GROUPWIDGET_H
#define GROUPWIDGET_H

#include <QWidget>

#include "DataEditorWidget.h"
#include "GlobalMessageBox.h"

namespace Ui {
class GroupWidget;
}

class GroupWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit GroupWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~GroupWidget();

    void saveData(bool signal=true);

    void connectSignals();

private:
    Ui::GroupWidget *ui;

    void updateControlsState();
    void updateFieldsValue();

    bool validateData();

private slots:
    void processFormsReply(QString form_type, QString data);
    void postResultReply(QString path);

    void btnSave_clicked();
    void btnUndo_clicked();

};

#endif // GROUPWIDGET_H
