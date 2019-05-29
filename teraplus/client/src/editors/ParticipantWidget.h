#ifndef PARTICIPANTWIDGET_H
#define PARTICIPANTWIDGET_H

#include <QWidget>
#include "DataEditorWidget.h"
#include "GlobalMessageBox.h"

namespace Ui {
class ParticipantWidget;
}

class ParticipantWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit ParticipantWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~ParticipantWidget();

    void saveData(bool signal=true);

    void connectSignals();

private:
    Ui::ParticipantWidget *ui;

    void updateControlsState();
    void updateFieldsValue();

    bool validateData();

private slots:
    void processFormsReply(QString form_type, QString data);

    void btnSave_clicked();
    void btnUndo_clicked();
};

#endif // PARTICIPANTWIDGET_H
