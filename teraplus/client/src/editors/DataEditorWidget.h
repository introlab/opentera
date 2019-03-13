#ifndef DATAEDITORWIDGET_H
#define DATAEDITORWIDGET_H

#include <QWidget>

#include "data/TeraData.h"
#include "data/TeraUser.h"

#include "ComManager.h"

class DataEditorWidget : public QWidget
{
    Q_OBJECT
public:
    explicit DataEditorWidget(ComManager* comMan, QWidget *parent = nullptr);
    ~DataEditorWidget();

    enum EditorState{
        STATE_READY=0,
        STATE_EDITING,
        STATE_WAITING,
        STATE_LOADING
    };

    void setData(const TeraData& data);
    TeraData* getData();

    virtual void saveData(bool signal=true)=0;
    virtual void undoData();
    virtual void deleteData()=0;
    virtual bool dataIsNew()=0;

    virtual void setReady();
    virtual void setEditing();
    virtual void setWaiting();
    virtual void setLoading();

    bool isReady();
    bool isEditing();
    bool isWaiting();
    bool isLoading();

    void refreshData();

private:
    virtual void updateControlsState()=0;
    virtual void updateFieldsValue()=0;
    virtual void updateAccessibleControls()=0;
    virtual bool validateData()=0;

protected:
    EditorState     m_editState;
    bool            m_undoing;

    ComManager*     m_comManager;

signals:
    void dataWasChanged();

    void stateEditing();
    void stateWaiting();
    void stateReady();
    void stateLoading();

    void closeRequest();

public slots:

    void setEditing(bool enabled);
    void undoOrDeleteData();

private slots:

};

#endif // DATAEDITORWIDGET_H
