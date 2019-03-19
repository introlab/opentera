#include "TeraForm.h"
#include "ui_TeraForm.h"

#include <QJsonDocument>
#include <QJsonParseError>
#include <QJsonArray>
#include <QJsonObject>
#include <QDebug>
#include <QVariantList>
#include <QVariantMap>

#include "Logger.h"

TeraForm::TeraForm(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::TeraForm)
{
    ui->setupUi(this);
}

TeraForm::~TeraForm()
{
    delete ui;
}

void TeraForm::buildUiFromStructure(const QString &structure)
{
    QJsonParseError json_error;

    QJsonDocument struct_info = QJsonDocument::fromJson(structure.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError){
        LOG_ERROR("Unable to parse Ui structure: " + json_error.errorString(), "TeraForm::buildUiFromStructure");
    }

    // Sections
    QVariantList struct_data = struct_info.array().toVariantList();
    int page_index = 0;
    for (QVariant section:struct_data){
        if (section.canConvert(QMetaType::QVariantMap)){
            QVariantMap section_data = section.toMap();
            if (page_index>0){
                QWidget* new_page = new QWidget(ui->toolboxMain);
                new_page->setObjectName("pageSection" + QString::number(page_index+1));
                ui->toolboxMain->addItem(new_page,"");
            }
            ui->toolboxMain->setItemText(page_index, section_data["label"].toString());
            page_index++;
        }
    }

}
