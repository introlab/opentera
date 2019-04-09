#ifndef SITEWIDGET_H
#define SITEWIDGET_H

#include <QWidget>

namespace Ui {
class SiteWidget;
}

class SiteWidget : public QWidget
{
    Q_OBJECT

public:
    explicit SiteWidget(QWidget *parent = nullptr);
    ~SiteWidget();

private:
    Ui::SiteWidget *ui;
};

#endif // SITEWIDGET_H
