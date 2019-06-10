#ifndef SESSIONTYPEWIDGET_H
#define SESSIONTYPEWIDGET_H

#include <QWidget>

#include "DataEditorWidget.h"
#include "GlobalMessageBox.h"

namespace Ui {
class SessionTypeWidget;
}

class SessionTypeWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit SessionTypeWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~SessionTypeWidget();

    void saveData(bool signal=true);

    void connectSignals();

private:
    Ui::SessionTypeWidget *ui;

    void updateControlsState();
    void updateFieldsValue();

    bool validateData();

private slots:
    void processFormsReply(QString form_type, QString data);
    void postResultReply(QString path);

    void btnSave_clicked();
    void btnUndo_clicked();

};

#endif // SESSIONTYPEWIDGET_H
