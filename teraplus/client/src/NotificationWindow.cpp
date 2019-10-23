#include "NotificationWindow.h"

#include <QMessageBox>
#include <QScreen>

NotificationWindow::NotificationWindow(QWidget *parent, NotificationType type, int level, int width, int height, int duration)
 : QWidget(parent), m_type(type), m_width(width), m_height(height), m_duration(duration),m_id(-1)
{
    setupUi(this);
    setWindowFlags(Qt::Window | Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint);

    setContentsMargins(0,0,0,0);

    //QDesktopWidget desktop;
    //or screenGeometry(), depending on your needs
    //QRect mainScreenSize = desktop.availableGeometry(desktop.primaryScreen());
    QRect mainScreenSize = QGuiApplication::primaryScreen()->availableGeometry();

    setGeometry(mainScreenSize.width() - m_width,
                mainScreenSize.height() - (level * m_height),
                m_width,
                m_height);

    setMinimumSize(m_width,m_height);
    setMaximumSize(m_width,m_height);


    //m_quickWidget->engine()->addImportPath("qrc:/notifications");

    switch (m_type)
    {
        case TYPE_MESSAGE:
            frameButtons->setVisible(false);
        break;

        case TYPE_YES_NO_QUESTION:
            //m_quickWidget->setSource(QUrl("qrc:notifications/YesNoQuestionNotification.qml"));
            frameButtons->setVisible(true);
        break;

        case TYPE_WARNING:
            //lblImg->setPixmap(QPixmap(":/pictures/warning1.png"));
            frameButtons->setVisible(false);
        break;

        default:
            qDebug("Not handled notification type : %i",m_type);
        break;
    }


    /*m_quickWidget->setContentsMargins(0,0,0,0);
    m_quickWidget->show();*/
    this->show();

    QPropertyAnimation *animate = new QPropertyAnimation(this,"windowOpacity",this);
    animate->setDuration(m_duration);
    animate->setStartValue(0.0);
    animate->setKeyValueAt(0.1, 0.8);
    animate->setKeyValueAt(0.9, 0.8);
    animate->setEndValue(0.0);
    animate->start(QAbstractAnimation::DeleteWhenStopped);

    connect(animate,SIGNAL(finished()),this,SLOT(animationFinished()));
    connect(btnClose,SIGNAL(clicked()),this,SLOT(notificationClosed()));
}

NotificationWindow::~NotificationWindow()
{
    emit notificationDestroyed(this);
}

void NotificationWindow::setNotificationText(const QString &message)
{
    m_text = message;
    lblText->setText(message);

    /*if (m_type==TYPE_WARNING){
        // Message box with the warning
        QMessageBox::warning(nullptr,"Attention!", m_text);
    }*/
}

void NotificationWindow::setNotificationID(int id)
{
    m_id = id;
    //emit setNotificationIdSignal(m_id);
}

int NotificationWindow::getNotificationID()
{
    return m_id;
}

QString NotificationWindow::getNotificationText()
{
    return m_text;
}

int NotificationWindow::getNotificationType()
{
    return m_type;
}

void NotificationWindow::resetPosition(int level)
{
    //QDesktopWidget desktop;
    //or screenGeometry(), depending on your needs
    //QRect mainScreenSize = desktop.availableGeometry(desktop.primaryScreen());
    QRect mainScreenSize = QGuiApplication::primaryScreen()->availableGeometry();

    setGeometry(mainScreenSize.width() - m_width,
                mainScreenSize.height() - (m_height * level),
                m_width,
                m_height);
}

void NotificationWindow::animationFinished()
{
    emit notificationFinished(this);
}

void NotificationWindow::notificationClosed()
{
    emit notificationClosed(this);
}

void NotificationWindow::hideEvent(QHideEvent *event)
{
    emit notificationHidden(this);
    QWidget::hideEvent(event);
}

void NotificationWindow::paintEvent(QPaintEvent *)
{
    //this is mandatory for the style sheet to take effect
     QStyleOption opt;
     opt.init(this);
     QPainter p(this);
     style()->drawPrimitive(QStyle::PE_Widget, &opt, &p, this);
}

void NotificationWindow::yesClicked(){
    emit notificationAnswer(this, "Yes");
}

void NotificationWindow::noClicked(){
    emit notificationAnswer(this, "No");
}
