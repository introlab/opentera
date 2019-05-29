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

    void setData(const QList<TeraData>& sessions, const QList<quint64>& filters, bool warning);

private:
    QDate m_currentDate;

    QList<TeraData>* m_sessions;
    QList<quint64>*      m_displayTypes;

    QHash<QDate,int>     m_dates;

    //QTableView *getView();

    //bool event(QEvent *event);
    //void mouseMoveEvent(QMouseEvent *ev);
signals:

public slots:

};

#endif // HISTORYCALENDARWIDGET_H
