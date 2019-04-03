#ifndef DATALISTWIDGET_H
#define DATALISTWIDGET_H

#include <QWidget>
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

    void setData(QList<TeraData*>* data);

    void addDataInList(TeraData* data, bool select_item=false);
    void selectItem(quint64 id);

private:
    Ui::DataListWidget*     ui;
    DataEditorWidget*       m_editor;
    QList<TeraData*>        m_datalist;
    ComManager*             m_comManager;
    TeraDataTypes           m_dataType;

    QListWidgetItem*        m_last_item;

    bool                    m_copying;
    bool                    m_searching;

    void updateDataInList(int index, TeraData* data, bool select_item=false);

    void setSearching(bool search);

public slots:


private slots:

};


#endif // DATALIST_WIDGET_H
