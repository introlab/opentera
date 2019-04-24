#include "KitWidget.h"
#include "ui_KitWidget.h"

KitWidget::KitWidget(ComManager *comMan, const TeraData *data, QWidget *parent) :
    DataEditorWidget(comMan, data, parent),
    ui(new Ui::KitWidget)
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
    queryDataRequest(WEB_FORMS_PATH, QUrlQuery(WEB_FORMS_QUERY_KIT));

}

KitWidget::~KitWidget()
{
    delete ui;
}

void KitWidget::saveData(bool signal)
{

}

void KitWidget::connectSignals()
{
    connect(m_comManager, &ComManager::formReceived, this, &KitWidget::processFormsReply);
}

void KitWidget::updateControlsState()
{

}

void KitWidget::updateFieldsValue()
{
    if (m_data && !hasPendingDataRequests()){
        if (!ui->wdgKit->formHasData())
            ui->wdgKit->fillFormFromData(m_data->toJson());
        else {
            ui->wdgKit->resetFormValues();
        }
    }
}

bool KitWidget::validateData()
{
    return ui->wdgKit->validateFormData();
}

void KitWidget::processFormsReply(QString form_type, QString data)
{
    if (form_type == WEB_FORMS_QUERY_KIT){
        ui->wdgKit->buildUiFromStructure(data);
        return;
    }
}
