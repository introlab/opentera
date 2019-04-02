#include "TeraForm.h"
#include "ui_TeraForm.h"

#include "Logger.h"
#include <QDebug>

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

    m_widgets.clear();

    QJsonObject struct_object = struct_info.object();
    //qDebug() << struct_info.object().keys();
    if (struct_object.contains("objecttype"))
        m_objectType = struct_object["objecttype"].toString();

    // Sections
    if (struct_object.contains("sections")){
        QVariantList struct_data =struct_object["sections"].toArray().toVariantList();
        int page_index = 0;
        for (QVariant section:struct_data){
            if (section.canConvert(QMetaType::QVariantMap)){
                QVariantMap section_data = section.toMap();
                if (page_index>0){
                    QWidget* new_page = new QWidget(ui->toolboxMain);
                    new_page->setObjectName("pageSection" + QString::number(page_index+1));
                    new_page->setStyleSheet("QWidget#" + new_page->objectName() + "{border: 1px solid white; border-radius: 5px;}");
                    ui->toolboxMain->addItem(new_page,"");
                }
                ui->toolboxMain->setItemText(page_index, section_data["label"].toString());
                if (section_data.contains("items")){
                    if (section_data["items"].canConvert(QMetaType::QVariantList)){
                        buildFormFromStructure(ui->toolboxMain->widget(page_index), section_data["items"].toList());
                    }
                }
                page_index++;
            }
        }
    }

}

void TeraForm::fillFormFromData(const QJsonObject &data)
{

    QVariantMap fields = data.toVariantMap();
    for (QString field:fields.keys()){
        if (m_widgets.contains(field)){
            setWidgetValue(m_widgets[field], fields[field]);
        } else{
           LOG_WARNING("No widget for field: " + field, "TeraForm::fillFormFromData");
        }
    }

}

void TeraForm::fillFormFromData(const QString &structure)
{
    if (structure.isEmpty())
        return;

    QJsonParseError json_error;

    QJsonDocument struct_info = QJsonDocument::fromJson(structure.toUtf8(), &json_error);
    if (json_error.error!= QJsonParseError::NoError){
        LOG_ERROR("Unable to parse Ui structure: " + json_error.errorString(), "TeraForm::fillFormFromData");
    }

    QJsonObject struct_object = struct_info.object();
    fillFormFromData(struct_object);

}

bool TeraForm::validateFormData(bool include_hidden)
{
    bool rval = true;
    for (QWidget* item:m_widgets.values()){
       rval &= validateWidget(item, include_hidden);
    }
    return rval;
}

QStringList TeraForm::getInvalidFormDataLabels(bool include_hidden)
{
    QStringList rval;
    for (QWidget* item:m_widgets.values()){
        if (!validateWidget(item, include_hidden)){
            rval.append(item->property("label").toString());
        }
    }
    return rval;
}

QWidget *TeraForm::getWidgetForField(const QString &field)
{
    if (m_widgets.contains(field))
        return m_widgets[field];

    return nullptr;
}

void TeraForm::buildFormFromStructure(QWidget *page, const QVariantList &structure)
{
    QFormLayout* layout = new QFormLayout(page);
    layout->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    for (QVariant item:structure){
        if (item.canConvert(QMetaType::QVariantMap)){
            QVariantMap item_data = item.toMap();
            QWidget* item_widget = nullptr;
            QLabel* item_label = new QLabel(item_data["label"].toString());
            QFrame* item_frame = new QFrame();
            QHBoxLayout* item_frame_layout = new QHBoxLayout();
            item_label->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
            item_frame->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
            item_frame_layout->addWidget(item_label);
            item_frame->setLayout(item_frame_layout);

            // Build widget according to item type
            QString item_type = item_data["type"].toString().toLower();
            if (item_type == "videoinputs"){
                item_widget = createVideoInputsWidget(item_data);
            }
            if (item_type == "audioinputs"){
                item_widget = createAudioInputsWidget(item_data);
            }
            if (item_type == "array"){
                item_widget = createArrayWidget(item_data);
            }
            if (item_type == "text"){
                item_widget = createTextWidget(item_data, false);
            }
            if (item_type == "password"){
                item_widget = createTextWidget(item_data, true);
            }
            if (item_type == "boolean"){
                item_widget = createBooleanWidget(item_data);
            }
            if (item_type == "numeric"){
                item_widget = createNumericWidget(item_data);
            }
            if (item_type == "hidden"){
                item_widget = createLabelWidget(item_data, true);
            }
            if (item_type == "checklist"){
                item_widget = createListWidget(item_data);
            }
            if (item_type == "longtext"){
                item_widget = createLongTextWidget(item_data);
            }
            if (item_type == "label"){
                item_widget = createLabelWidget(item_data, false);
            }


            if (item_widget){
                // Set widget properties
                if (item_data.contains("label"))
                    item_widget->setProperty("label", item_data["label"].toString());
                if (item_data.contains("id"))
                    item_widget->setProperty("id", item_data["id"]);
                if (item_data.contains("required")){
                    item_widget->setProperty("required", item_data["required"]);
                    item_label->setText("<font color=red>*</font> " + item_label->text());
                }
                if (item_data.contains("condition")){
                    item_widget->setProperty("condition", item_data["condition"]);
                    item_frame->setStyleSheet("background-color:darkgrey;");
                }
                if (item_data.contains("readonly")){
                    item_widget->setProperty("readonly", item_data["readonly"].toBool());
                    item_widget->setEnabled(item_data["readonly"].toBool());
                }

                item_widget->setMinimumHeight(30);

                // Add widget to layout
                layout->addRow(item_frame, item_widget);

                // Add widget to list
                m_widgets[item_data["id"].toString()] = item_widget;

                // Remove row if hidden
                if (item_type == "hidden"){
                    setWidgetVisibility(item_widget, nullptr, false);
                }

            }else{
                LOG_WARNING("Unknown item type: " + item_type, "TeraForm::buildFormFromStructure");
            }
        }
    }

    // Set layout alignement
    layout->setAlignment(Qt::AlignTop);
    page->setLayout(layout);

    // Set default values
    setDefaultValues();
    checkConditions();
    validateFormData(true);


}

void TeraForm::setDefaultValues()
{
    for (QWidget* item:m_widgets.values()){
        if (QComboBox* combo = dynamic_cast<QComboBox*>(item)){
            combo->setCurrentIndex(0);
        }
    }
}

QWidget *TeraForm::createVideoInputsWidget(const QVariantMap &structure)
{
    Q_UNUSED(structure)
    QComboBox* item_combo = new QComboBox();

    // Add empty item
    item_combo->addItem("", "");

    // Query webcams on the system
    QList<QCameraInfo> cameras = QCameraInfo::availableCameras();
    for (QCameraInfo camera:cameras){
        item_combo->addItem(camera.description(), camera.deviceName());
    }

    // Using old-style connect since SLOT has less parameter and not working with new-style connect
    connect(item_combo, SIGNAL(currentIndexChanged(int)), this, SLOT(widgetValueChanged()));

    return item_combo;
}

QWidget *TeraForm::createAudioInputsWidget(const QVariantMap &structure)
{
    Q_UNUSED(structure)
    QComboBox* item_combo = new QComboBox();

    // Add empty item
    item_combo->addItem("", "");

    // Query webcams on the system
    QList<QAudioDeviceInfo> inputs = QAudioDeviceInfo::availableDevices(QAudio::AudioInput);
    for (QAudioDeviceInfo input:inputs){
        item_combo->addItem(input.deviceName(), input.deviceName());
    }

    // Using old-style connect since SLOT has less parameter and not working with new-style connect
    connect(item_combo, SIGNAL(currentIndexChanged(int)), this, SLOT(widgetValueChanged()));

    return item_combo;
}

QWidget *TeraForm::createArrayWidget(const QVariantMap &structure)
{
    QComboBox* item_combo = new QComboBox();

    // Add empty item
    item_combo->addItem("", "");

    if (structure.contains("values")){
        if (structure["values"].canConvert(QMetaType::QVariantList)){
            for (QVariant value:structure["values"].toList()){
                if (value.canConvert(QMetaType::QVariantMap)){
                    QVariantMap item_data = value.toMap();
                    item_combo->addItem(item_data["value"].toString(), item_data["id"]);
                }
            }
        }

    }

    // Using old-style connect since SLOT has less parameter and not working with new-style connect
    connect(item_combo, SIGNAL(currentIndexChanged(int)), this, SLOT(widgetValueChanged()));

    return item_combo;
}

QWidget *TeraForm::createTextWidget(const QVariantMap &structure, bool is_masked)
{
    Q_UNUSED(structure)
    QLineEdit* item_text = new QLineEdit();

    if (is_masked)
        item_text->setEchoMode(QLineEdit::Password);

    connect(item_text, &QLineEdit::textChanged, this, &TeraForm::widgetValueChanged);

    return item_text;
}

QWidget *TeraForm::createBooleanWidget(const QVariantMap &structure)
{
    Q_UNUSED(structure)
    QCheckBox* item_check = new QCheckBox();
    item_check->setCursor(Qt::PointingHandCursor);

    connect(item_check, &QCheckBox::clicked, this, &TeraForm::widgetValueChanged);

    return item_check;
}

QWidget *TeraForm::createNumericWidget(const QVariantMap &structure)
{
    QSpinBox* item_spin = new QSpinBox();

    if (structure.contains("minimum")){
        item_spin->setMinimum(structure["minimum"].toInt());
    }else {
        item_spin->setMinimum(0);
    }

    if (structure.contains("maximum")){
        item_spin->setMaximum(structure["maximum"].toInt());
    }else{
        item_spin->setMaximum(99999);
    }

    // Using old-style connect since SLOT has less parameter and not working with new-style connect
    connect(item_spin, SIGNAL(valueChanged(int)), this, SLOT(widgetValueChanged()));

    return item_spin;
}

QWidget *TeraForm::createLabelWidget(const QVariantMap &structure, bool is_hidden)
{
    Q_UNUSED(structure)
    QLabel* item_label = new QLabel();

    item_label->setHidden(is_hidden);

    return item_label;
}

QWidget *TeraForm::createListWidget(const QVariantMap &structure)
{
    QListWidget* item_list = new QListWidget();

    if (structure.contains("values")){
        // TODO.
    }

    return item_list;
}

QWidget *TeraForm::createLongTextWidget(const QVariantMap &structure)
{
    Q_UNUSED(structure)
    QTextEdit* item_text = new QTextEdit();
    return item_text;
}

void TeraForm::checkConditions()
{
    for (QWidget* item:m_widgets.values()){
        if (!item)
            continue;
        checkConditionsForItem(item);
    }
}

void TeraForm::checkConditionsForItem(QWidget *item)
{
    if (item->property("condition").isValid()){
        // Item has a condition
        if (item->property("condition").canConvert(QMetaType::QVariantMap)){
            QVariantMap condition = item->property("condition").toMap();
            QString check_id = condition["item"].toString();
            if (!check_id.isNull()){
                QWidget* check_item = m_widgets[check_id];
                if (check_item){
                    if (check_item->property("condition").isValid())
                        checkConditionsForItem(check_item);
                    if (check_item->isHidden()){
                        setWidgetVisibility(item, check_item, false);
                        return;
                    }

                    // Check if condition is met or not for that item
                    QString op = condition["op"].toString();
                    QVariant value = condition["condition"];
                    QVariant sender_index;
                    QVariant sender_value;
                    getWidgetValues(check_item, &sender_index, &sender_value);

                    bool condition_met = false;
                    //TODO: Other operators...
                    if (op == "="){
                        if (sender_index == value || sender_value == value){
                            condition_met = true;
                        }
                    }

                    // Hide/show that item
                    //if (item->isVisible() != condition_met){
                        setWidgetVisibility(item, check_item, condition_met);
                        //qDebug() << "Hiding...";
                    //}
                }
            }
        }
    }

}

void TeraForm::setWidgetVisibility(QWidget *widget, QWidget *linked_widget, bool visible)
{

    if (widget->parentWidget()){
        if (QFormLayout* form_layout = dynamic_cast<QFormLayout*>(widget->parentWidget()->layout())){
            if (visible){
                // Check if is a removed row
                if (m_hidden_rows.contains(widget)){
                    QFormLayout::TakeRowResult row = m_hidden_rows[widget];
                    int parent_row;
                    if (linked_widget){
                        form_layout->getWidgetPosition(linked_widget, &parent_row, nullptr);
                    }else {
                        form_layout->getWidgetPosition(ui->toolboxMain, &parent_row, nullptr);
                    }
                    form_layout->insertRow(parent_row+1, row.labelItem->widget(), row.fieldItem->widget());
                    row.labelItem->widget()->show();
                    row.fieldItem->widget()->show();
                    m_hidden_rows.remove(widget);
                }
            }else{
                if (!m_hidden_rows.contains(widget)){
                    m_hidden_rows[widget] = form_layout->takeRow(widget);
                    widget->hide();
                    m_hidden_rows[widget].labelItem->widget()->hide();
                }
            }
        }
    }

}

void TeraForm::getWidgetValues(QWidget* widget, QVariant *id, QVariant *value)
{
    *id = QVariant("");

    if (QComboBox* combo = dynamic_cast<QComboBox*>(widget)){
        *id = combo->currentData();
        *value = combo->currentText();
    }

    if (QLineEdit* text = dynamic_cast<QLineEdit*>(widget)){
        *value = text->text();
    }

    if (QCheckBox* check = dynamic_cast<QCheckBox*>(widget)){
        *value = check->isChecked();
    }

    if (QSpinBox* spin = dynamic_cast<QSpinBox*>(widget)){
        *value = spin->value();
    }
}

void TeraForm::setWidgetValue(QWidget *widget, const QVariant &value)
{
    if (QComboBox* combo = dynamic_cast<QComboBox*>(widget)){
        int index = combo->findText(value.toString());
        if (index>=0){

        }else{
            LOG_WARNING("Item not found in ComboBox "+ combo->objectName() + " for item " + value.toString(), "TeraForm::setWidgetValue");
        }
        return;
    }

    if (QLineEdit* text = dynamic_cast<QLineEdit*>(widget)){
        text->setText(value.toString());
        return;
    }

    if (QTextEdit* text = dynamic_cast<QTextEdit*>(widget)){
        text->setText(value.toString());
        return;
    }

    if (QLabel* label = dynamic_cast<QLabel*>(widget)){
        label->setText(value.toString());
        return;
    }

    if (QCheckBox* check = dynamic_cast<QCheckBox*>(widget)){
        check->setChecked(value.toBool());
        return;
    }

    if (QSpinBox* spin = dynamic_cast<QSpinBox*>(widget)){
        spin->setValue(value.toInt());
        return;
    }

    LOG_WARNING("Unhandled widget: "+ QString(widget->metaObject()->className()) + " for item " + value.toString(), "TeraForm::setWidgetValue");
}

bool TeraForm::validateWidget(QWidget *widget, bool include_hidden)
{

    bool rval = true;

    if (widget->isVisibleTo(widget->parentWidget()) || include_hidden){
        if (widget->property("required").isValid()){
            if (widget->property("required").toBool()){
                QVariant id, value;
                getWidgetValues(widget, &id, &value);
                if (value.isNull() || id.isNull() || value.toInt()==-1 || value.toString().isEmpty()){
                    rval = false;
                }
            }
        }
    }

    if (rval){
        widget->setStyleSheet("");
    }else{
        widget->setStyleSheet("background-color: #ffaaaa;");
    }
    return rval;
}

void TeraForm::widgetValueChanged()
{
    // This will work only if the sender is in the same thread, which is always the case here.
    QObject* sender = QObject::sender();
    if (!sender)
        return;

    if (QWidget* sender_widget = dynamic_cast<QWidget*>(sender)){
        validateWidget(sender_widget);
    }

    checkConditions();

}
