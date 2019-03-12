#ifndef NOTIFICATION_WINDOW_H_
#define NOTIFICATION_WINDOW_H_

#include <QWidget>
#include <QPropertyAnimation>
#include <QPainter>
#include <QStyleOption>
#include <QDesktopWidget>
#include <QDebug>

#include "ui_notification.h"


namespace Ui {
class NotifyWindow;
}

class NotificationWindow : public QWidget, public Ui::NotifyWindow
{
    Q_OBJECT

    typedef enum {
        TYPE_MESSAGE,
        TYPE_YES_NO_QUESTION,
        TYPE_WARNING,
        TYPE_CUSTOM}
    NotificationType;

public:

    NotificationWindow(QWidget *parent, NotificationType type, int level = 1, int width = 400, int height = 100, int duration = 5000);

    ~NotificationWindow();

    void setNotificationText(const QString &message);

    void setNotificationID(int id);

    int getNotificationID();

    QString getNotificationText();

    int getNotificationType();

    void resetPosition(int level);

protected slots:

    void animationFinished();
    void notificationClosed();

    void yesClicked();
    void noClicked();

signals:

    //Standard signals
    void notificationFinished(NotificationWindow *window);
    void notificationHidden(NotificationWindow *window);
    void notificationClosed(NotificationWindow *window);
    void notificationDestroyed(NotificationWindow *window);
    void notificationAnswer(NotificationWindow *window, QString answer);

protected:

    virtual void hideEvent(QHideEvent * event);
    void paintEvent(QPaintEvent *);
    int m_type;
    int m_width;
    int m_height;
    int m_duration;
    int m_id;
    QString m_text;
    QVBoxLayout *m_layout;
};

#endif
