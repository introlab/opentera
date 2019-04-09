#ifndef SITEWIDGET_H
#define SITEWIDGET_H

#include <QWidget>

#include "DataEditorWidget.h"

namespace Ui {
class SiteWidget;
}

class SiteWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit SiteWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~SiteWidget();

private:
    Ui::SiteWidget *ui;

    void connectSignals();
};

#endif // SITEWIDGET_H
