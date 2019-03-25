#ifndef USERWIDGET_H
#define USERWIDGET_H

#include <QWidget>

#include "DataEditorWidget.h"
#include "data/TeraUser.h"

namespace Ui {
class UserWidget;
}

class UserWidget : public DataEditorWidget
{
    Q_OBJECT

public:
    explicit UserWidget(ComManager* comMan, const TeraUser& data = nullptr, QWidget *parent = nullptr);
    ~UserWidget();

    void setData(const TeraUser& data);
    TeraUser* getData();

    void saveData(bool signal=true);

    bool dataIsNew();

    void deleteData();

    void setWaiting();
    void setReady();

    void setLimited(bool limited);

    void connectSignals();

private:
    Ui::UserWidget* ui;

    TeraUser*   m_data;
    bool        m_limited; // Current user editing only

    void updateControlsState();
    void updateFieldsValue();
    void updateAccessibleControls();
    void hideValidationIcons();

    bool validateData();

    void hideProfileValidationIcons();
    bool validateProfile();
    void buildProfileFromUI();

public slots:


private slots:
    // Profile editor items
    void objectDefReceived(const QString &def, const QString &type);

    void btnEdit_clicked();
    void btnDelete_clicked();
    void btnSave_clicked();
    void txtPassword_textChanged(const QString &new_pass);
    void btnUndo_clicked();
};



#endif // USERWIDGET_H
