#include "TeraForm.h"
#include "ui_TeraForm.h"

#include "Logger.h"
#include <QDebug>

TeraForm::TeraForm(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::TeraForm)
{
    ui->setupUi(this);

    m_highlightConditionals = true;
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

    m_initialValues.clear();
    // Check if the object we need is part of that object or not.
    if (data.contains(m_objectType)){
        // Found it - extract data from it.
        m_initialValues = data[m_objectType].toObject().toVariantMap();
    }else{
        // If not, we suppose it is the object itself!
        m_initialValues = data.toVariantMap();
    }

    resetFormValues();

    // Set initial values for missing fields
    for (QString field:m_widgets.keys()){
        if (!m_initialValues.contains(field)){
            QVariant value;
            getWidgetValues(m_widgets[field],nullptr, &value);
            m_initialValues.insert(field, value);
        }
    }

}

void TeraForm::fillFormFromData(const QString &structure)
{
    QJsonDocument struct_info;
    QJsonParseError json_error;
    if (!structure.isEmpty()){
        struct_info = QJsonDocument::fromJson(structure.toUtf8(), &json_error);
    }else{
        struct_info = QJsonDocument::fromJson("{}", &json_error);
    }

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

bool TeraForm::setFieldValue(const QString &field, const QVariant &value)
{
    bool rval = false;

    if (m_widgets.contains(field)){
        setWidgetValue(m_widgets[field], value);
        rval = true;
    }

    return rval;
}

QVariant TeraForm::getFieldValue(const QString &field)
{
    QVariant rval;

    if (m_widgets.contains(field)){
        getWidgetValues(m_widgets[field], nullptr, &rval);
    }
    return rval;
}

void TeraForm::hideField(const QString &field)
{
    QWidget* widget = getWidgetForField(field);
    if (widget){
        QFormLayout* form_layout = dynamic_cast<QFormLayout*>(widget->parentWidget()->layout());

        m_hidden_rows[widget] = form_layout->takeRow(widget);
        widget->hide();
        m_hidden_rows[widget].labelItem->widget()->hide();
    }
}

QString TeraForm::getFormData(bool include_unmodified_data)
{
    QString data;
    QJsonDocument document = getFormDataJson(include_unmodified_data);
    data = document.toJson();
    return data;
}

QJsonDocument TeraForm::getFormDataJson(bool include_unmodified_data)
{
    QJsonDocument document;
    QJsonObject data_obj;
    QJsonObject base_obj;

    for(QString field:m_widgets.keys()){
        QVariant value, id;
        getWidgetValues(m_widgets[field], &id, &value);
        if (!id.isNull())
            value = id;
        // Include only modified fields or ids
        if ((!include_unmodified_data && m_initialValues[field] != value)
                || field.startsWith("id_") || include_unmodified_data){
            QJsonValue json_value = QJsonValue::fromVariant(value);
            if (field.startsWith("id_")){
                // Force value into int
                json_value = QJsonValue::fromVariant(value.toInt());
            }
            data_obj.insert(field, json_value);
        }
    }

    if (!data_obj.isEmpty()){
        base_obj.insert(m_objectType, data_obj);
        document.setObject(base_obj);
    }

    return document;
}

TeraData* TeraForm::getFormDataObject(const TeraDataTypes data_type)
{
    TeraData* rval = new TeraData(data_type);
    for(QString field:m_widgets.keys()){
        QVariant value, id;
        getWidgetValues(m_widgets[field], &id, &value);
        if (!id.isNull())
            value = id;
        rval->setFieldValue(field, value);
    }
    return rval;
}

QColor TeraForm::getGradientColor(const int &lower_thresh, const int &middle_thresh, const int &higher_thresh, const int &value)
{
    QColor lower_color = QColor(Qt::green).toHsv();
    QColor middle_color = QColor(232, 97, 0).toHsv(); // orange
    QColor higger_color = QColor(Qt::red).toHsv();

    QColor grad_color;
    qreal hue;
    qreal sat;
    qreal val;

    int current_value = value;

    if (current_value < lower_thresh)
        current_value = lower_thresh;
    if (current_value > higher_thresh)
        current_value = higher_thresh;

    if (current_value <= middle_thresh){
        qreal ratio = static_cast<qreal>(current_value-lower_thresh) / middle_thresh;
        hue = doLinearInterpolation(lower_color.hueF(), middle_color.hueF(), ratio);
        sat = doLinearInterpolation(lower_color.saturationF(), middle_color.saturationF(), ratio);
        val = doLinearInterpolation(lower_color.valueF(), middle_color.valueF(), ratio);
    }else{
        qreal ratio = static_cast<qreal>(current_value-middle_thresh) / static_cast<qreal>(higher_thresh-middle_thresh);
        hue = doLinearInterpolation(middle_color.hueF(), higger_color.hueF(), ratio);
        sat = doLinearInterpolation(middle_color.saturationF(), higger_color.saturationF(), ratio);
        val = doLinearInterpolation(middle_color.valueF(), higger_color.valueF(), ratio);
    }

    grad_color.setHsvF(hue, sat, val);

    return grad_color;

}

bool TeraForm::formHasData()
{
    return !m_initialValues.isEmpty();
}

void TeraForm::resetFormValues()
{
    for (QString field:m_initialValues.keys()){
        if (m_widgets.contains(field)){
            setWidgetValue(m_widgets[field], m_initialValues[field]);
        } else{
           LOG_WARNING("No widget for field: " + field, "TeraForm::resetFormValues");
        }
    }

}

void TeraForm::setHighlightConditions(const bool &hightlight)
{
    m_highlightConditionals = hightlight;
}

void TeraForm::buildFormFromStructure(QWidget *page, const QVariantList &structure)
{
    QFormLayout* layout = new QFormLayout(page);
    layout->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);
    //layout->setFieldGrowthPolicy(QFormLayout::ExpandingFieldsGrow);
    layout->setVerticalSpacing(3);
    layout->setAlignment(Qt::AlignTop);

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
                item_widget = createLabelWidget(item_data);
            }
            if (item_type == "checklist"){
                item_widget = createListWidget(item_data);
            }
            if (item_type == "longtext"){
                item_widget = createLongTextWidget(item_data);
            }
            if (item_type == "label"){
                item_widget = createLabelWidget(item_data);
            }
            if (item_type == "color"){
                item_widget = createColorWidget(item_data);
            }
            if (item_type == "datetime"){
                item_widget = createDateTimeWidget(item_data);
            }
            if (item_type == "duration"){
                item_widget = createDurationWidget(item_data);
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
                }else{
                    item_label->setText("  " + item_label->text());
                }
                if (item_data.contains("condition")){
                    item_widget->setProperty("condition", item_data["condition"]);
                    if (m_highlightConditionals)
                        item_frame->setStyleSheet("background-color:darkgrey;");
                }
                if (item_data.contains("readonly")){
                    item_widget->setProperty("readonly", item_data["readonly"].toBool());
                    item_widget->setDisabled(item_data["readonly"].toBool());
                }
                item_widget->setProperty("item_type", item_type);

                item_widget->setMinimumHeight(25);

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
        //item_combo->addItem(camera.description(), camera.deviceName());
        item_combo->addItem(camera.description(), camera.description());
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
                    item_combo->addItem(item_data["value"].toString(), item_data["id"].toString());
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

    if (structure.contains("max_length")){
        item_text->setMaxLength(structure["max_length"].toInt());
    }

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

QWidget *TeraForm::createLabelWidget(const QVariantMap &structure)
{
    Q_UNUSED(structure)
    QLabel* item_label = new QLabel();

    //item_label->setHidden(is_hidden);

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

QWidget *TeraForm::createColorWidget(const QVariantMap &structure)
{
    Q_UNUSED(structure)
    QPushButton* item_btn = new QPushButton();

    item_btn->setFlat(true);
    item_btn->setProperty("color", "#FFFFFF");
    item_btn->setStyleSheet("background-color: #FFFFFF");
    item_btn->setCursor(Qt::PointingHandCursor);
    item_btn->setMaximumWidth(100);

    // Connect signal
    connect(item_btn, &QPushButton::clicked, this, &TeraForm::colorWidgetClicked);

    return item_btn;
}

QWidget *TeraForm::createDateTimeWidget(const QVariantMap &structure)
{
    Q_UNUSED(structure)
    QDateTimeEdit* item_dt = new QDateTimeEdit();
    item_dt->setDisplayFormat("dd MMMM yyyy - hh:mm");
    item_dt->setCalendarPopup(true);

    return item_dt;

}

QWidget *TeraForm::createDurationWidget(const QVariantMap &structure)
{
    Q_UNUSED(structure)
    QTimeEdit* item_t = new QTimeEdit();
    item_t->setDisplayFormat("hh:mm:ss");

    return item_t;
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
                    if (check_item->isHidden() && check_item->property("item_type").toString()!="hidden"){
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
                    if (op == "<>"){
                        if (sender_index != value || sender_value != value){
                            condition_met = true;
                        }
                    }
                    if (op.toUpper() == "NOT NULL"){
                        if (!sender_index.isNull() || !sender_value.isNull())
                            condition_met = true;
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
/*    if (id)
        *id = QVariant();*/

    if (QComboBox* combo = dynamic_cast<QComboBox*>(widget)){
        if (id)
            *id = combo->currentData();
        *value = combo->currentText();
    }

    if (QLineEdit* text = dynamic_cast<QLineEdit*>(widget)){
        *value = text->text();
    }

    if (QTextEdit* text = dynamic_cast<QTextEdit*>(widget)){
        *value = text->toPlainText();
        return;
    }

    if (QCheckBox* check = dynamic_cast<QCheckBox*>(widget)){
        *value = check->isChecked();
    }

    if (QSpinBox* spin = dynamic_cast<QSpinBox*>(widget)){
        *value = spin->value();
    }

    if (QLabel* label = dynamic_cast<QLabel*>(widget)){
        *value = label->text();
    }

    if (QPushButton* btn = dynamic_cast<QPushButton*>(widget)){
        if (btn->property("color").isValid()){
            *value = btn->property("color").toString();
        }
    }

    if (QDateTimeEdit* dt = dynamic_cast<QDateTimeEdit*>(widget)){
        *value = dt->dateTime();
    }

    if (QTimeEdit* te = dynamic_cast<QTimeEdit*>(widget)){
        if (te->property("item_type") == "duration"){
            *value = QTime(0,0).secsTo(te->time());
        }else{
            *value = te->time();
        }
    }

    if (value->canConvert(QMetaType::QString)){
        bool ok;
        QString string_val = value->toString();
        string_val.toInt(&ok);
        if (ok){
            *value = string_val.toInt();
        }

        if (string_val.startsWith("{")){
            // Maybe JSON, so try to keep that format if possible
            QJsonParseError err;
            QJsonDocument doc = QJsonDocument::fromJson(string_val.toUtf8(), &err);
            if (err.error == QJsonParseError::NoError){
                *value = doc;
            }
        }

    }
}

QVariant TeraForm::getWidgetValue(QWidget *widget)
{
    QVariant value;
    QVariant id;

    getWidgetValues(widget, &id, &value);

    if (!id.isNull())
        value = id;

    return value;

}

void TeraForm::setWidgetValue(QWidget *widget, const QVariant &value)
{
    if (QComboBox* combo = dynamic_cast<QComboBox*>(widget)){
        int index = combo->findText(value.toString());
        if (index>=0){
            combo->setCurrentIndex(index);
        }else{
            // Check if the value matches a data field
            index = combo->findData(value);
            if (index>=0){
                combo->setCurrentIndex(index);
            }else{
                // Check if we have a number, if so, suppose it is the index
                if (value.canConvert(QMetaType::Int)){
                    index = value.toInt();
                    if (index>=0 && index+1<combo->count()){
                        combo->setCurrentIndex(index+1);
                        return;
                    }
                }
                LOG_WARNING("Item not found in ComboBox "+ combo->objectName() + " for item " + value.toString(), "TeraForm::setWidgetValue");
            }
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

    if (QPushButton* btn = dynamic_cast<QPushButton*>(widget)){
        if (value.toString().startsWith("#")){
            btn->setProperty("color", value.toString());
            btn->setStyleSheet(QString("background-color: " + value.toString() + ";"));
            return;
        }

    }

    if (QTimeEdit* te = dynamic_cast<QTimeEdit*>(widget)){
        QTime time_value = value.toTime();

        if (!time_value.isValid()){
            int time_s = value.toInt();
            time_value = QTime(0,0).addSecs(time_s);
        }
        te->setTime(time_value);
        return;
    }

    if (QDateTimeEdit* dt = dynamic_cast<QDateTimeEdit*>(widget)){
        QDateTime time_value = value.toDateTime();

        if (!time_value.isValid()){
            unsigned int time_s = value.toUInt();
            // Consider we have a UNIX timestamp
            time_value = QDateTime::fromSecsSinceEpoch(time_s);
        }

        dt->setDateTime(value.toDateTime());
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
                if (value.isNull() || value.toInt()==-1 || value.toString().isEmpty()){
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

qreal TeraForm::doLinearInterpolation(const qreal &p1, const qreal &p2, const qreal &value)
{
    return (p1 + (p2-p1)*value);
}

void TeraForm::widgetValueChanged()
{
    // This will work only if the sender is in the same thread, which is always the case here.
    QObject* sender = QObject::sender();
    if (!sender)
        return;

    QWidget* sender_widget = dynamic_cast<QWidget*>(sender);
    if (sender_widget){
        validateWidget(sender_widget);
        emit widgetValueHasChanged(sender_widget, getWidgetValue(sender_widget));
    }

    checkConditions();



}

void TeraForm::colorWidgetClicked()
{
    QObject* sender = QObject::sender();
    if (!sender)
        return;

    QPushButton* sender_widget = dynamic_cast<QPushButton*>(sender);

    QColorDialog diag;
    QColor color;

    color = diag.getColor(QColor(sender_widget->property("color").toString()),nullptr,tr("Choisir la couleur"));

    if (color.isValid()){
        sender_widget->setProperty("color", color.name());
        // Display current color
        sender_widget->setStyleSheet(QString("background-color: " + color.name() + ";"));
    }
}
