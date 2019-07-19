#ifndef SITEWIDGET_H
#define SITEWIDGET_H

#include <QWidget>
#include <QListWidgetItem>
#include <QTableWidgetItem>

#include "DataEditorWidget.h"
#include "GlobalMessageBox.h"

namespace Ui {
class SiteWidget;
}

class SiteWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit SiteWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~SiteWidget();

    void saveData(bool signal=true);

    void setData(const TeraData* data);

private slots:
    void processFormsReply(QString form_type, QString data);
    void processSiteAccessReply(QList<TeraData> access);
    void processUsersReply(QList<TeraData> users);
    void processProjectsReply(QList<TeraData> projects);
    void processDevicesReply(QList<TeraData> devices);

    void btnSave_clicked();
    void btnUndo_clicked();
    void btnUpdateAccess_clicked();
    void btnProjects_clicked();
    void btnDevices_clicked();
    void btnUsers_clicked();

private:
    Ui::SiteWidget *ui;

    QMap<int, int>               m_tableUsers_ids_rows;
    QMap<int, QListWidgetItem*>  m_listProjects_items;
    QMap<int, QTableWidgetItem*> m_listDevices_items;

    QDialog*                    m_diag_editor;

    void connectSignals();

    void updateSiteAccess(const TeraData* access);
    void updateProject(const TeraData* project);
    void updateDevice(const TeraData* device);

    void updateControlsState();
    void updateFieldsValue();
    bool validateData();
};

#endif // SITEWIDGET_H
