#include "TeraSessionStatus.h"

TeraSessionStatus::TeraSessionStatus(QObject *parent) : QObject(parent)
{

}

QString TeraSessionStatus::getStatusName(const TeraSessionStatus::SessionStatus &status)
{
    switch(status){
    case STATUS_CANCELLED:
        return tr("Annulée");
    case STATUS_COMPLETED:
        return tr("Complétée");
    case STATUS_INPROGRESS:
        return tr("En cours");
    case STATUS_NOTSTARTED:
        return tr("Planifiée");
    case STATUS_TERMINATED:
        return tr("Interrompue");
    }
    return tr("");
}

QString TeraSessionStatus::getStatusName(const int &status)
{
    return getStatusName(static_cast<SessionStatus>(status));
}

QString TeraSessionStatus::getStatusColor(const TeraSessionStatus::SessionStatus &status)
{
    switch(status){
    case STATUS_CANCELLED:
        return "cyan";
    case STATUS_COMPLETED:
        return "lightgreen";
    case STATUS_INPROGRESS:
        return "yellow";
    case STATUS_TERMINATED:
        return "red";
    case STATUS_NOTSTARTED:
        return "white";
    }
    return "black";
}

QString TeraSessionStatus::getStatusColor(const int &status)
{
    return getStatusColor(static_cast<SessionStatus>(status));
}
