#include "ConfigManager.h"

ConfigManager::ConfigManager(QObject *parent) : QObject(parent)
{

}

ConfigManager::ConfigManager(QString filename, QObject *parent) : QObject(parent)
{
    m_filename = filename;
}

void ConfigManager::setFilename(QString filename)
{
    m_filename = filename;
}

QString ConfigManager::getFilename()
{
    return m_filename;
}

bool ConfigManager::loadConfig()
{
    m_lastJsonError.error = QJsonParseError::NoError;

    QFile configFile(m_filename);
    // Open the config file
    if (!configFile.open(QIODevice::ReadOnly | QIODevice::Text))
        return false;
    // Read all the data in the config file - size is minimal, so loading in memory is fine.
    QByteArray configData = configFile.readAll();
    configFile.close();

    // Convert data into JSON array, if possible.
    m_config = QJsonDocument::fromJson(configData, &m_lastJsonError);
    if (m_lastJsonError.error!= QJsonParseError::NoError)
        return false;

    return true;

}

QJsonParseError ConfigManager::getLastError()
{
    return m_lastJsonError;
}

bool ConfigManager::hasParseError()
{
    return (m_lastJsonError.error != QJsonParseError::NoError);
}



