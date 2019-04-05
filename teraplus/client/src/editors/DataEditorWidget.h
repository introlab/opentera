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
    virtual void processQueryReply(const QString &path, const QUrlQuery &query_args, const QString &data)=0;
    bool hasPendingDataRequests();

    void postDataRequest(const QString &path, const QString &query_args);
    virtual void processPostReply(const QString &path, const QString &data)=0;

private:
    virtual void updateControlsState()=0;
    virtual void updateFieldsValue()=0;
    virtual bool validateData()=0;

    QString getQueryDataName(const QString &path, const QUrlQuery &query_args);

    QList<QString>  m_requests;
    ComManager*     m_comManager;

    EditorState     m_editState;
protected:
    bool            m_undoing;
    TeraData*       m_data;

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
    void queryDataReply(const QString &path, const QUrlQuery &query_args, const QString &data);
    void postDataReply(const QString &path, const QString &data);
    void comDataError(QNetworkReply::NetworkError error, QString error_str);
};

#endif // DATAEDITORWIDGET_H
