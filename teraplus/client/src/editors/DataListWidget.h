#ifndef DATALISTWIDGET_H
#define DATALISTWIDGET_H

#include <QWidget>
#include <QJsonDocument>

#include "DataEditorWidget.h"

#include "TeraData.h"

//#include "TeraMenu_gui.h"
#include "ui_DataListWidget.h"

#include "editors/UserWidget.h"

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

private:
    Ui::DataListWidget*                 ui;
    DataEditorWidget*                   m_editor;
    QMap<TeraData*, QListWidgetItem*>   m_datamap;
    ComManager*                         m_comManager;
    TeraDataTypes                       m_dataType;

    bool                                m_copying;
    bool                                m_searching;
    bool                                m_newdata;

    void connectSignals();
    void queryDataList();

    TeraData *getCurrentData();
    QListWidgetItem *getItemForData(TeraData *data);
    void updateDataInList(TeraData *data, bool select_item=false);
    void deleteDataFromList(TeraData* data);
    void showEditor(TeraData *data);

    void setSearching(bool search);

    void clearDataList();

public slots:


private slots:
    void com_Waiting(bool waiting);
    void com_NetworkError(QNetworkReply::NetworkError error, QString error_str);

    void deleteDataReply(QString path, int id);
    void setDataList(QList<TeraData> list);

    void editor_dataDeleted();
    void editor_dataChanged();

    void searchChanged(QString new_search);
    void clearSearch();
    void lstData_currentItemChanged(QListWidgetItem *current, QListWidgetItem *previous);

    void newDataRequested();
    void deleteDataRequested();
    void copyDataRequested();
};


#endif // DATALIST_WIDGET_H
