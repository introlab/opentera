#ifndef KITWIDGET_H
#define KITWIDGET_H

#include <QWidget>
#include "DataEditorWidget.h"

namespace Ui {
class KitWidget;
}

class KitWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit KitWidget(ComManager* comMan, const TeraData* data = nullptr, QWidget *parent = nullptr);
    ~KitWidget();

    void saveData(bool signal);

private:
    Ui::KitWidget *ui;

    void connectSignals();

    // DataEditorWidget interface
    void updateControlsState();
    void updateFieldsValue();
    bool validateData();

private slots:
    void processFormsReply(QString form_type, QString data);
};

#endif // KITWIDGET_H
