#ifndef DATAEDITORWIDGET_H
#define DATAEDITORWIDGET_H

#include <QWidget>

#include "data/TeraData.h"

#include "ComManager.h"

class DataEditorWidget : public QWidget
{
    Q_OBJECT
public:
    explicit DataEditorWidget(ComManager *comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~DataEditorWidget();

    enum EditorState{
        STATE_READY=0,
        STATE_EDITING,
        STATE_WAITING,
        STATE_LOADING
    };

    virtual void setData(const TeraData *data);
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
    bool isWaitingOrLoading();

    void refreshData();

    void queryDataRequest(const QString &path, const QUrlQuery &query_args = QUrlQuery());
    bool hasPendingDataRequests();
    void postDataRequest(const QString &path, const QString &query_args);

private:
    virtual void updateControlsState()=0;
    virtual void updateFieldsValue()=0;
    virtual bool validateData()=0;

    QString getQueryDataName(const QString &path, const QUrlQuery &query_args);

    QList<QString>  m_requests;

    EditorState     m_editState;
protected:
    bool            m_undoing;
    TeraData*       m_data;
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
    void queryDataReplyOK(const QString &path, const QUrlQuery &query_args);
    void postDataReplyOK(const QString &path);
    void comDataError(QNetworkReply::NetworkError error, QString error_str);
};

#endif // DATAEDITORWIDGET_H
