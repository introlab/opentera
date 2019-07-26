#include "GlobalMessageBox.h"

#include <QAbstractButton>
#include <QDebug>

GlobalMessageBox::GlobalMessageBox(QWidget *parent) :
    QMessageBox(parent)
{

    // Initialize look and feel
    setStyleSheet(//"QWidget{background-color: rgba(0,0,0,0);color:white;border-radius:5px}"
                  "QMessageBox{background-color:rgba(10,10,10,100%); color:white;}"
                  "QMessageBox QLabel{color:white; font-size:10pt;}"
                  "QMessageBox QPushButton{min-height:30px; min-width:75px;}");
                         /*"QMessageBox QPushButton{background-color:rgb(80,80,80); max-width:200px;"
                         "border:1px solid rgba(255,255,255,50%);min-width:50px;min-height:32px;}"
                         "QPushButton:hover{background-color:  rgba(255,255,255,75%);color:black;}");*/

    m_xPressed=false;
}

GlobalMessageBox::~GlobalMessageBox()
{

}

QMessageBox::StandardButton GlobalMessageBox::showYesNo(const QString &title, const QString &text){

   /* QPixmap image;
    image.load(":/pictures/UnknownSystem.png");

    setIconPixmap(image.scaled(48,48));*/
    setIcon(QMessageBox::Question);
    setWindowTitle(title);
    setText(text);
    setModal(true);

    setStandardButtons(QMessageBox::Yes | QMessageBox::No);
    setButtonText(QMessageBox::Yes,tr("Oui"));
    setButtonText(QMessageBox::No,tr("Non"));
    button(QMessageBox::Yes)->setIcon(QIcon("://icons/ok.png"));
    button(QMessageBox::Yes)->setCursor(Qt::PointingHandCursor);
    button(QMessageBox::No)->setIcon(QIcon("://icons/error.png"));
    button(QMessageBox::No)->setCursor(Qt::PointingHandCursor);
    setDefaultButton(QMessageBox::No);

    exec();
    if (m_xPressed){
        m_xPressed=false;
        return QMessageBox::NoButton;

    }
    return standardButton(clickedButton());

}

void GlobalMessageBox::showWarning(const QString &title, const QString &text){
    setIcon(QMessageBox::Warning);
    setWindowTitle(title);
    setTextFormat(Qt::RichText);
    QString display_text = text;
    display_text.replace("\n","<br>");
    setText(display_text);
    setModal(true);
    setStandardButtons(QMessageBox::Ok);
    button(QMessageBox::Ok)->setCursor(Qt::PointingHandCursor);
    exec();
}

void GlobalMessageBox::showError(const QString &title, const QString &text)
{
    setIcon(QMessageBox::Critical);
    setWindowTitle(title);
    setTextFormat(Qt::RichText);
    QString display_text = text;
    display_text.replace("\n","<br>");
    setText(display_text);
    setModal(true);
    setStandardButtons(QMessageBox::Ok);
    button(QMessageBox::Ok)->setCursor(Qt::PointingHandCursor);
    exec();
}

void GlobalMessageBox::showInfo(const QString &title, const QString &text)
{
    setIcon(QMessageBox::Information);
    setWindowTitle(title);
    setTextFormat(Qt::RichText);
    QString display_text = text;
    display_text.replace("\n","<br>");
    setText(display_text);
    setModal(true);
    setStandardButtons(QMessageBox::Ok);
    button(QMessageBox::Ok)->setCursor(Qt::PointingHandCursor);
    exec();
}

void GlobalMessageBox::closeEvent(QCloseEvent *evt){
    if (clickedButton() == nullptr)
        m_xPressed = true;

    QMessageBox::closeEvent(evt);

}


/*QString GlobalMessageBox::getIcon(MessageTypes msg_type){
    QString icon = "";

    switch (msg_type){
    case MSG_INFO:
        icon = ":/pictures/flag1.png";
        break;
    case MSG_EXCLAMATION:
        icon = ":/pictures/notification.png";
        break;
    case MSG_QUESTION:
        icon = ":/pictures/UnknownSystem.png";
        break;
    case MSG_WARNING:
        icon = ":/pictures/warning1.png";
        break;
    }

    return icon;


}*/
