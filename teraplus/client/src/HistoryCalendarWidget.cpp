#include "HistoryCalendarWidget.h"
#include <QTextCharFormat>

HistoryCalendarWidget::HistoryCalendarWidget(QWidget *parent) :
    QCalendarWidget(parent)
{
    m_currentDate = QDate::currentDate();

    //setStyleSheet("QWidget{background-color: white; color: black;}");

}

HistoryCalendarWidget::~HistoryCalendarWidget(){

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
    if (!m_dates.contains(date) || date.month() != monthShown()){
        // Paint with default format
        QCalendarWidget::paintCell (painter, rect, date);
        return;
    }

    painter->save(); // save standard settings

    // TODO: Adjust!
   /* QList<SessionInfo*>* sessions = m_sessions->at(m_dates.value(date))->getSessions();
    bool has_alert_today = false;
    for (int i=0; i<sessions->count(); i++){
        if (sessions->at(i)->hasTechAlert()){
            has_alert_today=true;
            break;
        }
    }

    if (date<=QDate::currentDate()){
         if (!has_alert_today){
            brush.setColor(QColor::fromRgb(255,255,255,198));
            pen.setColor(QColor::fromRgb(255,255,255,128));
         }else{
             brush.setColor(QColor::fromRgb(255,100,100,198));
             pen.setColor(QColor::fromRgb(255,100,100,128));
         }
    }else{
        brush.setColor(QColor::fromRgb(255,255,255,128));
        pen.setColor(QColor::fromRgb(255,255,255,64));
    }

    painter->setPen(pen);
    painter->setBrush(brush);
    painter->drawRect(rect.adjusted(2,2,-2,-2));

    QHash<quint64,QString> to_display;

    for (int i=0; i<sessions->count();i++){
        quint64 ses_type = sessions->at(i)->sessionType();
        if (m_displayTypes)
            if (!m_displayTypes->contains(ses_type))
                continue;
        if (to_display.contains(ses_type))
            continue;
        // We have a session that we need to display, find color for the correct session type
        for (int j=0; j<m_sessionsTypes->count(); j++){
            if (m_sessionsTypes->at(j)->id()==ses_type){
                to_display.insert(ses_type,m_sessionsTypes->at(j)->color());
                break;
            }
        }
    }
    quint8 count = 0;
    quint8 total = to_display.count(); //m_sessions->at(m_dates.value(date))->sessionsTypesCount(*m_displayTypes);
    //qDebug() << date.toString() << ": Count = " << QString::number(count) << ", Total = " << QString::number(total);

    for (int i=0; i<to_display.count(); i++){
        QColor color(to_display.values().at(i));
        //qDebug() << date.toString() << ": Count = " << QString::number(count) << ", Total = " << QString::number(total) << ", Color = " << to_display.values().at(i);
        pen.setColor(color);
        brush.setColor(color);
        painter->setPen(pen);
        painter->setBrush(brush);

        //Draw the indicator
        float ratio = (float)count/(float)total;
        painter->drawRect(rect.adjusted(2,ratio*rect.height()+2,-2*(float)rect.width()/3-2,rect.height()/(float)total-2));

        count++;
    }*/

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

void HistoryCalendarWidget::setData(const QList<TeraData>& sessions, const QList<quint64>& filters, bool warning){
    /*m_sessions = sessions;
    m_displayTypes = filters;

    // Create dates mapping for fast search
    m_dates.clear();
    for (int i=0; i<m_sessions->count(); i++){
        if (m_displayTypes==NULL || m_sessions->at(i)->hasSessionTypes(*m_displayTypes)){
            m_dates.insert(m_sessions->at(i)->date(),i);

            // Remove alerts from display if not tech access
            if (!tech){
                for (int j=0; j<m_sessions->at(i)->sessionsCount(); j++){
                    m_sessions->at(i)->getSessions()->at(j)->setTechAlert(false);
                }
            }
        }
    }

    updateCells();*/
}

