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
    void processKitsReply(QList<TeraData> kits);

    void btnSave_clicked();
    void btnUndo_clicked();
    void btnUpdateAccess_clicked();

private:
    Ui::SiteWidget *ui;

    QMap<int, int>               m_tableUsers_ids_rows;
    QMap<int, QListWidgetItem*>  m_listProjects_items;
    QMap<int, QTableWidgetItem*> m_listKits_items;

    void connectSignals();

    void updateSiteAccess(const TeraData* access);
    void updateProject(const TeraData* project);
    void updateKit(const TeraData* kit);

    void updateControlsState();
    void updateFieldsValue();
    bool validateData();
};

#endif // SITEWIDGET_H
