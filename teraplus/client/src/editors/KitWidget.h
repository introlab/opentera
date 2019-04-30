#ifndef KITWIDGET_H
#define KITWIDGET_H

#include <QWidget>
#include <QListWidgetItem>

#include "DataEditorWidget.h"

namespace Ui {
class KitWidget;
}

class KitWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit KitWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~KitWidget();

    void saveData(bool signal=true);

private:
    Ui::KitWidget                   *ui;
    QList<TeraData>                 m_projects;
    QMap<int, QListWidgetItem*>     m_listDevices_items;
    QMap<int, QListWidgetItem*>     m_listParticipants_items;
    QMap<int, TeraData*>            m_ids_devices;

    void connectSignals();

    void updateDevice(const TeraData* device);
    void updateParticipant(const TeraData* participant);

    // DataEditorWidget interface
    void updateControlsState();
    void updateFieldsValue();
    bool validateData();

private slots:
    void processFormsReply(QString form_type, QString data);
    void processProjectsReply(QList<TeraData> projects);
    void processDevicesReply(QList<TeraData> devices);
    void processKitDevicesReply(QList<TeraData> kit_devices);
    void processParticipantsReply(QList<TeraData> participants);
    void processDeleteDataReply(QString path, int id);

    void wdgKitWidgetValueChanged(QWidget* widget, QVariant value);
    void lstDeviceCurrentChanged(QListWidgetItem* current, QListWidgetItem* previous);
    void lstKitDeviceCurrentChanged(QListWidgetItem* current, QListWidgetItem* previous);

    void btnSave_clicked();
    void btnUndo_clicked();
    void btnAddDevice_clicked();
    void btnDelDevice_clicked();
};

#endif // KITWIDGET_H
