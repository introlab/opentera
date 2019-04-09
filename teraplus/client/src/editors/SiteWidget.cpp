#include "SiteWidget.h"
#include "ui_SiteWidget.h"

SiteWidget::SiteWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::SiteWidget)
{
    if (parent){
        ui->setupUi(parent);
    }else {
        ui->setupUi(this);
    }
    setAttribute(Qt::WA_StyledBackground); //Required to set a background image

    // Connect signals and slots
    connectSignals();

    // Query forms definition

    // Query sites and projects

    setData(data);
}

SiteWidget::~SiteWidget()
{
    delete ui;
}

void SiteWidget::connectSignals()
{

}
