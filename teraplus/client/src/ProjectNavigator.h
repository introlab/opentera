#ifndef PROJECTNAVIGATOR_H
#define PROJECTNAVIGATOR_H

#include <QWidget>
#include <QAction>
#include <QMenu>

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
    void connectSignals();

private:
    Ui::ProjectNavigator *ui;
    ComManager* m_comManager;
    int m_currentSiteId;

    // Ui items
    QList<QAction*> m_newItemActions;
    QMenu*          m_newItemMenu;

    QAction* addNewItemAction(const TeraDataTypes &data_type, const QString& label);

private slots:
     void newItemRequested();

     void processSitesReply(QList<TeraData> sites);

     void currentSiteChanged();
     void btnEditSite_clicked();

signals:
     void dataDisplayRequest(TeraDataTypes data_type, int data_id);
};

#endif // PROJECTNAVIGATOR_H
