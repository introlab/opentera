#ifndef PARTICIPANTWIDGET_H
#define PARTICIPANTWIDGET_H

#include <QWidget>
#include <QTableWidgetItem>

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

    QMap<int, QTableWidgetItem*>    m_listSessions_items;
    QMap<int, TeraData*>            m_ids_session_types;

    void updateControlsState();
    void updateFieldsValue();

    bool validateData();

    void updateSession(const TeraData* session);

private slots:
    void processFormsReply(QString form_type, QString data);
    void processSessionsReply(QList<TeraData> sessions);
    void processSessionTypesReply(QList<TeraData> session_types);

    void btnSave_clicked();
    void btnUndo_clicked();
};

#endif // PARTICIPANTWIDGET_H
