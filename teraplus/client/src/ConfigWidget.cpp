#include "ConfigWidget.h"
#include "ui_ConfigWidget.h"

ConfigWidget::ConfigWidget(ComManager *comMan, QWidget *parent) :
    QWidget(parent),  
    ui(new Ui::ConfigWidget),
    m_comManager(comMan)
{
    if (parent){
        ui->setupUi(parent);
    }else {
        ui->setupUi(this);
    }

    m_dataListEditor = nullptr;

    // Set default layout for widget editor, if needed
    if (ui->wdgEditor->layout() == nullptr){
        ui->wdgEditor->setLayout(new QHBoxLayout);
    }

    setupSections();

    connectSignals();

}

ConfigWidget::~ConfigWidget()
{
    delete ui;
}

void ConfigWidget::addSection(const QString &name, const QIcon &icon, const int &id)
{
    QListWidgetItem *tmp = new QListWidgetItem(ui->lstSections);
    tmp->setIcon(icon);

    tmp->setText(name);
    tmp->setTextAlignment(Qt::AlignCenter);
    tmp->setFlags(Qt::ItemIsSelectable | Qt::ItemIsEnabled);
    tmp->setData(Qt::UserRole,id);
}

void ConfigWidget::setupSections()
{
    addSection(tr("Utilisateurs"), QIcon(TeraData::getIconFilenameForDataType(TERADATA_USER)), TERADATA_USER);
    addSection(tr("Sites"), QIcon("://icons/site.png"), TERADATA_SITE);
    //addSection(tr("Appareils"), QIcon(TeraData::getIconFilenameForDataType(TERADATA_DEVICE)), TERADATA_DEVICE);
    addSection(tr("Kits"), QIcon(TeraData::getIconFilenameForDataType(TERADATA_KIT)), TERADATA_KIT);
    addSection(tr("Séances"), QIcon(TeraData::getIconFilenameForDataType(TERADATA_SESSIONTYPE)), TERADATA_SESSIONTYPE);
    addSection(tr("Évaluations"), QIcon(TeraData::getIconFilenameForDataType(TERADATA_TESTDEF)), TERADATA_TESTDEF);

    ui->lstSections->setItemSelected(ui->lstSections->item(0),true);
}

void ConfigWidget::currentSectionChanged(QListWidgetItem *current, QListWidgetItem *previous)
{
    Q_UNUSED(previous)
    TeraDataTypes current_section = static_cast<TeraDataTypes>(current->data(Qt::UserRole).toInt());

    //qDebug() << current_section;

    if (m_dataListEditor){
        ui->wdgEditor->layout()->removeWidget(m_dataListEditor);
        m_dataListEditor->deleteLater();
    }

    m_dataListEditor = new DataListWidget(m_comManager, current_section);
    ui->wdgEditor->layout()->addWidget(m_dataListEditor);

}

void ConfigWidget::com_Waiting(bool waiting)
{
    setDisabled(waiting);
}

void ConfigWidget::connectSignals()
{
    connect(ui->lstSections, &QListWidget::currentItemChanged, this, &ConfigWidget::currentSectionChanged);
    connect(m_comManager, &ComManager::waitingForReply, this, &ConfigWidget::com_Waiting);
    connect(ui->btnClose, &QPushButton::clicked, this, &ConfigWidget::closeRequest);
}
