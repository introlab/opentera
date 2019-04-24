#ifndef DEVICEWIDGET_H
#define DEVICEWIDGET_H

#include <QWidget>

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

    void updateControlsState();
    void updateFieldsValue();
    bool validateData();

    void connectSignals();

private slots:
    void processFormsReply(QString form_type, QString data);
    void processKitDevicesReply(QList<TeraData> kit_devices);

    void btnSave_clicked();
    void btnUndo_clicked();

};

#endif // DEVICEWIDGET_H
