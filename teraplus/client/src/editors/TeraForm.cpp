#include "TeraForm.h"
#include "ui_TeraForm.h"

#include <QJsonDocument>
#include <QJsonParseError>
#include <QJsonArray>
#include <QJsonObject>
#include <QDebug>
#include <QVariantList>

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
    QVariantList test = struct_info.array().toVariantList();
    qDebug() << test;
/*    for (QJsonValue section:struct_info.array()){

    }*/

}
