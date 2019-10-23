#include "BaseDialog.h"
#include <QSizePolicy>
#include <QVBoxLayout>

BaseDialog::BaseDialog(QWidget *parent)
    : QDialog(parent)
{
    m_ui.setupUi(this);

    m_centralWidgetLayout = new QVBoxLayout(m_ui.centralWidget);
    m_centralWidgetLayout->setMargin(0);
    m_centralWidgetLayout->setContentsMargins(0,0,0,0);

}

void BaseDialog::setCentralWidget(QWidget *widget)
{
    widget->setParent(m_ui.centralWidget);
    m_centralWidgetLayout->addWidget(widget);
    //widget->setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::MinimumExpanding);
}

