#ifndef SESSIONWIDGET_H
#define SESSIONWIDGET_H

#include <QWidget>
#include <QTableWidgetItem>

#include "DataEditorWidget.h"
#include "GlobalMessageBox.h"

#include "TeraSessionStatus.h"
#include "TeraSessionEvent.h"
#include "DownloadedFile.h"
#include "BaseDialog.h"

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

    QMap<int, QTableWidgetItem*> m_listDeviceDatas;
    QMap<int, QTableWidgetItem*> m_listSessionEvents;

    void updateControlsState();
    void updateFieldsValue();

    bool validateData();

    void updateParticipant(TeraData* participant);
    void updateDeviceData(TeraData* device_data);
    void updateEvent(TeraData* event);

private slots:
    void btnSave_clicked();
    void btnUndo_clicked();
    void btnDownload_clicked();
    void btnDeleteData_clicked();
    void btnDownloadAll_clicked();

    void processFormsReply(QString form_type, QString data);
    void processParticipantsReply(QList<TeraData> participants);
    void processDeviceDatasReply(QList<TeraData> device_datas);
    void processSessionEventsReply(QList<TeraData> events);
    void postResultReply(QString path);
    void deleteDataReply(QString path, int id);

    void onDownloadCompleted(DownloadedFile* file);

    void currentSelectedDataChanged(QTableWidgetItem* current, QTableWidgetItem* previous);
};

#endif // SESSIONWIDGET_H
