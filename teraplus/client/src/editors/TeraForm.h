#ifndef TERAFORM_H
#define TERAFORM_H

#include <QWidget>

namespace Ui {
class TeraForm;
}

class TeraForm : public QWidget
{
    Q_OBJECT

public:
    explicit TeraForm(QWidget *parent = nullptr);
    ~TeraForm();

    void buildUiFromStructure(const QString& structure);

private:
    Ui::TeraForm *ui;


};

#endif // TERAFORM_H
