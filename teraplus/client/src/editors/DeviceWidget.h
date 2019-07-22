#ifndef DEVICEWIDGET_H
#define DEVICEWIDGET_H

#include <QWidget>
#include <QListWidgetItem>

#include "DataEditorWidget.h"

namespace Ui {
class DeviceWidget;
}

class DeviceWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit DeviceWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~DeviceWidget();

    void saveData(bool signal=true);

private:
    Ui::DeviceWidget *ui;

    QMap<int, QListWidgetItem*>  m_listSites_items;
    QMap<int, QListWidgetItem*>  m_listDeviceSites_items;
    QMap<int, QListWidgetItem*>  m_listParticipants_items;
    QMap<int, QListWidgetItem*>  m_listSessionTypes_items;

    void updateControlsState();
    void updateFieldsValue();
    bool validateData();

    void connectSignals();

    void updateSite(TeraData *site);
    void updateParticipant(TeraData *participant);
    void updateSessionType(TeraData *session_type);

private slots:
    void processFormsReply(QString form_type, QString data);
    void processSitesReply(QList<TeraData> sites);
    void processDeviceSitesReply(QList<TeraData> device_sites);
    void processDeviceParticipantsReply(QList<TeraData> device_parts);
    void processSessionTypesReply(QList<TeraData> session_types);

    void btnSave_clicked();
    void btnUndo_clicked();
    void btnSaveSites_clicked();

};

#endif // DEVICEWIDGET_H
