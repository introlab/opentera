#ifndef HISTORYCALENDARWIDGET_H
#define HISTORYCALENDARWIDGET_H

#include <QCalendarWidget>
#include <QPainter>
#include <QDate>
#include <QList>

#include "TeraData.h"

class HistoryCalendarWidget : public QCalendarWidget
{
    Q_OBJECT
public:
    explicit HistoryCalendarWidget(QWidget *parent=nullptr);
    ~HistoryCalendarWidget();

    void paintCell(QPainter *painter, const QRect &rect, const QDate &date) const;

    //void setEvents1(QList<QDate>* events);
    //void setEvents2(QList<QDate>* events);

    void setData(const QList<TeraData* > &sessions);
    void setSessionTypes(const QList<TeraData *> &session_types);
    void setFilters(const QList<int> &session_types_ids);

private:
    QDate m_currentDate;

    QMultiMap<QDate, TeraData*>     m_sessions;
    QList<int>                      m_displayTypes;
    QMap<int, TeraData*>            m_ids_session_types;

    //QTableView *getView();

    //bool event(QEvent *event);
    //void mouseMoveEvent(QMouseEvent *ev);
signals:

public slots:

};

#endif // HISTORYCALENDARWIDGET_H
