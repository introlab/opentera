#ifndef GROUPWIDGET_H
#define GROUPWIDGET_H

#include <QWidget>

#include <QTableWidgetItem>

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

    QMap<int, QTableWidgetItem*> m_listParticipants_items;

    void updateControlsState();
    void updateFieldsValue();

    void updateParticipant(TeraData* participant);

    bool validateData();

private slots:
    void processFormsReply(QString form_type, QString data);
    void postResultReply(QString path);
    void processParticipants(QList<TeraData> participants);

    void btnSave_clicked();
    void btnUndo_clicked();

};

#endif // GROUPWIDGET_H
