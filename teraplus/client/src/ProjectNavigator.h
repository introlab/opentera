#ifndef PROJECTNAVIGATOR_H
#define PROJECTNAVIGATOR_H

#include <QWidget>
#include <QAction>
#include <QMenu>

#include <QTreeWidgetItem>

#include "ComManager.h"

namespace Ui {
class ProjectNavigator;
}

class ProjectNavigator : public QWidget
{
    Q_OBJECT

public:
    explicit ProjectNavigator(QWidget *parent = nullptr);
    ~ProjectNavigator();

    void setComManager(ComManager* comMan);

    void initUi();

    int getCurrentSiteId() const;
    int getCurrentProjectId() const;

    void selectItem(const TeraDataTypes& data_type, const int& id);
    void removeItem(const TeraDataTypes& data_type, const int& id);

    void setOnHold(const bool& hold);

private:
    Ui::ProjectNavigator        *ui;
    ComManager*                 m_comManager;
    int                         m_currentSiteId;
    int                         m_currentProjectId;
    int                         m_currentGroupId;

    bool                        m_selectionHold;

    QMap<int, QTreeWidgetItem*> m_projects_items;
    QMap<int, QTreeWidgetItem*> m_groups_items;
    QMap<int, QTreeWidgetItem*> m_participants_items;

    void updateSite(const TeraData* site);
    void updateProject(const TeraData* project);
    void updateGroup(const TeraData* group);
    void updateParticipant(const TeraData* participant);

    void updateAvailableActions(QTreeWidgetItem *current_item);
    TeraDataTypes getItemType(QTreeWidgetItem* item);

    void connectSignals();

    // Ui items
    QList<QAction*> m_newItemActions;
    QMenu*          m_newItemMenu;

    QAction* addNewItemAction(const TeraDataTypes &data_type, const QString& label);
    QAction* getActionForDataType(const TeraDataTypes &data_type);

private slots:
     void newItemRequested();
     void deleteItemRequested();

     void processSitesReply(QList<TeraData> sites);
     void processProjectsReply(QList<TeraData> projects);
     void processGroupsReply(QList<TeraData> groups);
     void processParticipantsReply(QList<TeraData> participants);

     void currentSiteChanged();
     void currentNavItemChanged(QTreeWidgetItem* current, QTreeWidgetItem* previous);
     void navItemExpanded(QTreeWidgetItem* item);
     void btnEditSite_clicked();

signals:
     void dataDisplayRequest(TeraDataTypes data_type, int data_id);
     void dataDeleteRequest(TeraDataTypes data_type, int data_id);
};

#endif // PROJECTNAVIGATOR_H
