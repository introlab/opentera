#ifndef SESSIONWIDGET_H
#define SESSIONWIDGET_H

#include <QWidget>

#include "DataEditorWidget.h"
#include "GlobalMessageBox.h"

#include "TeraSessionStatus.h"

namespace Ui {
class SessionWidget;
}

class SessionWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit SessionWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~SessionWidget();

    void saveData(bool signal=true);

    void connectSignals();
private:
    Ui::SessionWidget *ui;

    void updateControlsState();
    void updateFieldsValue();

    bool validateData();

    void updateParticipant(TeraData* participant);

private slots:
    void btnSave_clicked();
    void btnUndo_clicked();


    void processFormsReply(QString form_type, QString data);
    void processParticipantsReply(QList<TeraData> participants);
    void postResultReply(QString path);
};

#endif // SESSIONWIDGET_H
