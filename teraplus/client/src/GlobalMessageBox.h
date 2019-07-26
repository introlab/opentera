#ifndef GLOBALMESSAGEBOX_H
#define GLOBALMESSAGEBOX_H

#include <QMessageBox>
#include <QCloseEvent>

class GlobalMessageBox : public QMessageBox
{
    Q_OBJECT

public:
    explicit GlobalMessageBox(QWidget *parent = nullptr);
    ~GlobalMessageBox();

    StandardButton showYesNo(const QString& title, const QString& text);
    void showWarning(const QString& title, const QString& text);
    void showError(const QString& title, const QString& text);
    void showInfo(const QString& title, const QString& text);


private:
    void closeEvent(QCloseEvent *evt);

    bool m_xPressed;
};

#endif // GLOBALMESSAGEBOX_H
