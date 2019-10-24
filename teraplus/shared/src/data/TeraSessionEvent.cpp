#include "TeraSessionEvent.h"

TeraSessionEvent::TeraSessionEvent(QObject *parent) : QObject(parent)
{

}

QString TeraSessionEvent::getEventTypeName(const TeraSessionEvent::SessionEventType &event)
{
    switch(event){
        case(GENERAL_ERROR):
            return tr("Erreur");
        case(GENERAL_INFO):
            return tr("Information");
        case(GENERAL_WARNING):
            return tr("Avertissement");
        case(SESSION_START):
            return tr("Début");
        case(SESSION_STOP):
            return tr("Fin");
        case(DEVICE_ON_CHARGE):
            return tr("Chargement - Début");
        case(DEVICE_OFF_CHARGE):
            return tr("Chargement - Fin");
        case(DEVICE_LOW_BATT):
            return tr("Pile faible");
        case(DEVICE_STORAGE_LOW):
            return tr("Espace disque faible");
        case(DEVICE_STORAGE_FULL):
            return tr("Espace disque plein");
        case(DEVICE_EVENT):
            return tr("Événement");
        case(USER_EVENT):
            return tr("Marque");
    }

    return tr("Inconnu");
}

QString TeraSessionEvent::getEventTypeName(const int &event)
{
    return getEventTypeName(static_cast<SessionEventType>(event));
}

QString TeraSessionEvent::getIconFilenameForEventType(const TeraSessionEvent::SessionEventType &event)
{
    switch(event){
        case(GENERAL_ERROR):
        case(DEVICE_STORAGE_FULL):
            return "://icons/error.png";
        case(GENERAL_INFO):
        case(DEVICE_EVENT):
        case(USER_EVENT):
            return "://icons/info.png";

        case(SESSION_START):
            return "://status/status_ok.png";
        case(SESSION_STOP):
            return "://status/status_notok.png";
        case(DEVICE_ON_CHARGE):
        case(DEVICE_OFF_CHARGE):
            return "://status/status_incomplete.png";
        case(GENERAL_WARNING):
        case(DEVICE_LOW_BATT):
        case(DEVICE_STORAGE_LOW):
            return "://icons/warning.png";

    }
    return "";
}

QString TeraSessionEvent::getIconFilenameForEventType(const int &event)
{
    return getIconFilenameForEventType(static_cast<SessionEventType>(event));
}
