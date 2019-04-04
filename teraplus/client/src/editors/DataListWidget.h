#ifndef DATALISTWIDGET_H
#define DATALISTWIDGET_H

#include <QWidget>
#include <QJsonDocument>

#include "DataEditorWidget.h"

#include "TeraData.h"

//#include "TeraMenu_gui.h"
#include "ui_DataListWidget.h"

//Data widgets
//#include "UserWidget.h"

namespace Ui {
class DataListWidget;
}

class DataListWidget :  public QWidget
{
    Q_OBJECT

public:
    explicit DataListWidget(ComManager* comMan, TeraDataTypes data_type, QWidget *parent = nullptr);
    ~DataListWidget();

    void selectItem(quint64 id);

private:
    Ui::DataListWidget*                 ui;
    DataEditorWidget*                   m_editor;
    QMap<TeraData*, QListWidgetItem*>   m_datamap;
    QList<TeraData*>                    m_datalist;
    ComManager*                         m_comManager;
    TeraDataTypes                       m_dataType;

    bool                    m_copying;
    bool                    m_searching;

    void connectSignals();
    void queryDataList();

    void updateDataInList(TeraData *data, const bool select_item=false);

    void setSearching(bool search);

    void clearDataList();

public slots:


private slots:
    void com_Waiting(bool waiting);
    void queryDataReply(const QString &path, const QUrlQuery &query_args, const QString &data);

    void searchChanged(QString new_search);
    void clearSearch();
};


#endif // DATALIST_WIDGET_H
