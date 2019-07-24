#include "DeviceAssignDialog.h"
#include "ui_DeviceAssignDialog.h"

DeviceAssignDialog::DeviceAssignDialog(ComManager *comMan, int device_id, QWidget *parent) :
    QDialog(parent),
    ui(new Ui::DeviceAssignDialog),
    m_comManager(comMan),
    m_id_device(device_id)
{
    ui->setupUi(this);

    connectSignals();

    // Query participants for device
    QUrlQuery args;
    args.addQueryItem(WEB_QUERY_ID_DEVICE, QString::number(m_id_device));
    m_comManager->doQuery(WEB_DEVICEPARTICIPANTINFO_PATH, args);
}

DeviceAssignDialog::~DeviceAssignDialog()
{
    delete ui;
}

QList<int> DeviceAssignDialog::getDeviceParticipantsIds()
{
    return m_id_device_participants;
}

void DeviceAssignDialog::connectSignals()
{
    connect(ui->btnCancel, &QPushButton::clicked, this, &DeviceAssignDialog::btnCancel_clicked);
    connect(ui->btnAdd, &QPushButton::clicked, this, &DeviceAssignDialog::btnAdd_clicked);
    connect(ui->btnDeassign, &QPushButton::clicked, this, &DeviceAssignDialog::btnDeassign_clicked);

    connect(m_comManager, &ComManager::deviceParticipantsReceived, this, &DeviceAssignDialog::processDeviceParticipants);
}

void DeviceAssignDialog::processDeviceParticipants(QList<TeraData> device_participants)
{
    if(ui->lstParticipants->count()==0){
        for (TeraData device_part:device_participants){
            if (device_part.getFieldValue("id_device").toInt() == m_id_device){
                QListWidgetItem* item = new QListWidgetItem(QIcon(TeraData::getIconFilenameForDataType(TERADATA_PARTICIPANT)),
                                                            device_part.getFieldValue("participant_name").toString());
                ui->lstParticipants->addItem(item);
                m_id_device_participants.append(device_part.getId());
            }
        }
    }
}

void DeviceAssignDialog::btnCancel_clicked()
{
    reject();
    setResult(ReturnCodes::DEVICEASSIGN_CANCEL);
}

void DeviceAssignDialog::btnAdd_clicked()
{
    accept();
    setResult(ReturnCodes::DEVICEASSIGN_ADD);
}

void DeviceAssignDialog::btnDeassign_clicked()
{
    accept();
    setResult(ReturnCodes::DEVICEASSIGN_DEASSIGN);
}
