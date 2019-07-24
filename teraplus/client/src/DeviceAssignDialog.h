#ifndef DEVICEASSIGNDIALOG_H
#define DEVICEASSIGNDIALOG_H

#include <QDialog>

#include "ComManager.h"

namespace Ui {
class DeviceAssignDialog;
}

class DeviceAssignDialog : public QDialog
{
    Q_OBJECT



public:
    explicit DeviceAssignDialog(ComManager* comMan, int device_id, QWidget *parent = nullptr);
    ~DeviceAssignDialog();

    enum ReturnCodes{
        DEVICEASSIGN_CANCEL = 2,
        DEVICEASSIGN_ADD = 3,
        DEVICEASSIGN_DEASSIGN = 4
    };

    QList<int> getDeviceParticipantsIds();

private:
    Ui::DeviceAssignDialog *ui;

    ComManager*     m_comManager;
    int m_id_device;

    QList<int>      m_id_device_participants;

    void connectSignals();

private slots:
    void processDeviceParticipants(QList<TeraData> device_participants);

    void btnCancel_clicked();
    void btnAdd_clicked();
    void btnDeassign_clicked();

};

#endif // DEVICEASSIGNDIALOG_H
