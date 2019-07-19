#ifndef ProjectWidget_H
#define ProjectWidget_H

#include <QWidget>
#include <QListWidgetItem>
#include <QTableWidgetItem>

#include "DataEditorWidget.h"
#include "GlobalMessageBox.h"

namespace Ui {
class ProjectWidget;
}

class ProjectWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit ProjectWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~ProjectWidget();

    void saveData(bool signal=true);

    void setData(const TeraData* data);

private slots:
    void processFormsReply(QString form_type, QString data);
    void processProjectAccessReply(QList<TeraData> access);
    void processUsersReply(QList<TeraData> users);
    void processGroupsReply(QList<TeraData> groups);
    void processDevicesReply(QList<TeraData> devices);

    void btnSave_clicked();
    void btnUndo_clicked();
    void btnUpdateAccess_clicked();
    void btnDevices_clicked();
    void btnUsers_clicked();

private:
    Ui::ProjectWidget *ui;

    QMap<int, int>               m_tableUsers_ids_rows;
    QMap<int, QListWidgetItem*>  m_listGroups_items;
    QMap<int, QTableWidgetItem*> m_listDevices_items;

    QDialog*                     m_diag_editor;

    void connectSignals();

    void updateProjectAccess(const TeraData* access);
    void updateGroup(const TeraData* group);
    void updateDevice(const TeraData* device);

    void updateControlsState();
    void updateFieldsValue();
    bool validateData();
};

#endif // ProjectWidget_H
