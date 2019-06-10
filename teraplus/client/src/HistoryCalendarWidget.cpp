#include "HistoryCalendarWidget.h"
#include "Logger.h"
#include <QTextCharFormat>

HistoryCalendarWidget::HistoryCalendarWidget(QWidget *parent) :
    QCalendarWidget(parent)
{
    m_currentDate = QDate::currentDate();

    //setStyleSheet("QWidget{background-color: white; color: black;}");

}

HistoryCalendarWidget::~HistoryCalendarWidget(){
    qDeleteAll(m_ids_session_types);
}

void HistoryCalendarWidget::paintCell(QPainter *painter, const QRect &rect, const QDate &date) const{
    QPen pen;
    QBrush brush;
    brush.setColor(Qt::transparent);
    brush.setStyle(Qt::SolidPattern);
    pen.setStyle(Qt::SolidLine);
    pen.setWidth(2);

    // Highlight current date
    /*if (date==m_currentDate){
        pen.setColor(Qt::darkGreen);
        //brush.setColor(Qt::darkGreen);

        painter->save(); // save standard settings
        painter->setPen(pen);
        painter->setBrush(brush);
        //painter->drawEllipse(rect.adjusted(2,2,-2,-2));
        //painter->drawRect(rect.adjusted(2,2,-2,-2));
        painter->drawText(rect, Qt::AlignCenter, QString::number(date.day()));
        painter->restore(); // restore previous settings
        //return;
    }*/

    if (date==QDate::currentDate()){
        pen.setColor(Qt::cyan);
        painter->setPen(pen);
        painter->drawText(rect, Qt::AlignCenter, QString::number(date.day()));
    }

    // Check for sessions on that date
    if (!m_sessions.keys().contains(date) || date.month() != monthShown()){
        // Paint with default format
        QCalendarWidget::paintCell (painter, rect, date);
        return;
    }

    painter->save(); // save standard settings

    // TODO: Adjust!
    QList<TeraData*> sessions = m_sessions.values(date);
    /*bool has_alert_today = false;
    for (int i=0; i<sessions->count(); i++){
        if (sessions->at(i)->hasTechAlert()){
            has_alert_today=true;
            break;
        }
    }*/

    if (date<=QDate::currentDate()){
         //if (!has_alert_today){
            brush.setColor(QColor::fromRgb(255,255,255,198));
            pen.setColor(QColor::fromRgb(255,255,255,128));
         /*}else{
             brush.setColor(QColor::fromRgb(255,100,100,198));
             pen.setColor(QColor::fromRgb(255,100,100,128));
         }*/
    }else{
        brush.setColor(QColor::fromRgb(255,255,255,128));
        pen.setColor(QColor::fromRgb(255,255,255,64));
    }

    painter->setPen(pen);
    painter->setBrush(brush);
    painter->drawRect(rect.adjusted(2,2,-2,-2));

    QHash<int,QString> display_colors;

    for (int i=0; i<sessions.count();i++){
        int ses_type = sessions.at(i)->getFieldValue("id_session_type").toInt();
        if (!m_displayTypes.contains(ses_type))
            continue;
        if (display_colors.contains(ses_type))
            continue;
        // We have a session that we need to display, find color for the correct session type
        if (m_ids_session_types.contains(ses_type)){
            display_colors[ses_type] = m_ids_session_types.value(ses_type)->getFieldValue("session_type_color").toString();
        }else{
            LOG_WARNING("No session type match - ignoring.", "HistoryCalendarWidget::paintCell");
        }
    }
    int count = 0;
    int total = display_colors.count(); //m_sessions->at(m_dates.value(date))->sessionsTypesCount(*m_displayTypes);
    //qDebug() << date.toString() << ": Count = " << QString::number(count) << ", Total = " << QString::number(total);

    for (int i=0; i<display_colors.count(); i++){
        QColor color(display_colors.values().at(i));
        //qDebug() << date.toString() << ": Count = " << QString::number(count) << ", Total = " << QString::number(total) << ", Color = " << to_display.values().at(i);
        pen.setColor(color);
        brush.setColor(color);
        painter->setPen(pen);
        painter->setBrush(brush);

        //Draw the indicator
        float ratio = static_cast<float>(count)/total;
        painter->drawRect(rect.adjusted(2,
                                        static_cast<int>(ratio*rect.height()+2),
                                        static_cast<int>(-2*static_cast<float>(rect.width())/3-2),
                                        static_cast<int>(rect.height()/static_cast<float>(total)-2)));
        count++;
    }

    // Check if we need to display any indicator warning for that session
    /*for (int i=0; i<sessions->count(); i++){
        if (sessions->at(i)->hasTechAlert()){
            painter->drawImage(rect.adjusted((float)rect.width()/2,2,-2,-(float)rect.height()/2),QImage(":/pictures/icons/warning.png"));
        }
    }*/

    pen.setColor(Qt::black);
    painter->setPen(pen);
    painter->drawText(rect, Qt::AlignCenter, QString::number(date.day()));
    painter->restore(); // restore previous settings
}

void HistoryCalendarWidget::setData(const QList<TeraData *> &sessions){
    qDeleteAll(m_sessions);
    m_sessions.clear();
    for (TeraData* ses:sessions){
        QDate session_date = ses->getFieldValue("session_start_datetime").toDateTime().date();
        if (session_date.isValid())
            m_sessions.insertMulti(session_date, new TeraData(*ses));
        else
            LOG_WARNING("Invalid session date", "HistoryCalendarWidget::setData");
    }

    updateCells();
}

void HistoryCalendarWidget::setSessionTypes(const QList<TeraData *> &session_types)
{
    qDeleteAll(m_ids_session_types);
    m_ids_session_types.clear();
    for (TeraData* st:session_types){
        m_ids_session_types[st->getId()] = new TeraData(*st);
    }
}

void HistoryCalendarWidget::setFilters(const QList<int> &session_types_ids)
{
    m_displayTypes = session_types_ids;
    updateCells();
}

