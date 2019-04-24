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

    QAction* addNewItemAction(const TeraDataTypes &data_type, const QString& label);

    ComManager* m_comManager;

    // Ui items
    QList<QAction*> m_newItemActions;
    QMenu*          m_newItemMenu;

private slots:
     void newItemRequested();

     void processSitesReply(QList<TeraData> sites);
};

#endif // PROJECTNAVIGATOR_H