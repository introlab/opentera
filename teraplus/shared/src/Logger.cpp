#include "Logger.h"
#include <QtDebug>
#include <QMutexLocker>
#include <QCoreApplication>


//Singleton
Logger* Logger::m_instance = nullptr;
QMutex  Logger::m_mutex(QMutex::Recursive);
Logger::ActivationPriority Logger::m_active_priority = Logger::DISABLE_PRIORITY; //DISABLE_PRIORITY; //INFO_PRIORITY; //


Logger* Logger::instance(const QString &path)
{
	QMutexLocker locker(&m_mutex);
	if (!m_instance)
	{	
		m_instance = new Logger(path);
	}
		
	return m_instance;
}

void Logger::destroy()
{
	QMutexLocker locker(&m_mutex);
	if (m_instance)
	{
		delete m_instance;
	}
    m_instance = nullptr;
}

Logger::Logger(const QString &path)
	: m_file(path)
{
	if (!m_file.open(QIODevice::WriteOnly| QIODevice::Text | QIODevice::Append))
	{
		qDebug("Cannot open log file");
	}
	else
	{
		logINFO("Log file opened : " + path ,"Logger");
	}

}

Logger::~Logger()
{
	if (m_file.isOpen())
	{
		logINFO("Log file closed","Logger");
	}

	m_file.close();
}

void Logger::setRedirectionActivation(bool state)
{
	QMutexLocker locker(&m_mutex);
	//Uninstall previous message redirection
    qInstallMessageHandler(nullptr);
	if(state)
	{
        qInstallMessageHandler(loggerMessageOutput);
	}
}

void Logger::setLogPriorityLevel(ActivationPriority priority)
{
	QMutexLocker locker(&m_mutex);
	m_active_priority = priority;
}

void Logger::logDEBUG(const QString &message, const QString &sender)
{
	QMutexLocker locker(&m_mutex);
    if(DEBUG_PRIORITY >= m_active_priority)
	{
		QTextStream out(&m_file);
		out << currentDateTimeString() << " [DEBUG] "<< " {"<<sender<<"} -- "<<message << "\n";
        fprintf(stderr,"{%s}:DEBUG [%s]: %s \n",QCoreApplication::applicationName().toStdString().c_str(), sender.toStdString().c_str(), message.toStdString().c_str());
		emit newLogEntry(DEBUG_PRIORITY,message,sender);
    }
}

void Logger::logSTATISTIC(const QString &message, const QString &sender)
{
    QMutexLocker locker(&m_mutex);
    if(STATISTIC_PRIORITY >= m_active_priority)
    {
        QTextStream out(&m_file);
        out << currentDateTimeString() << " [STATISTIC] "<< " {"<<sender<<"} -- "<<message << "\n";
        fprintf(stderr,"{%s}:STATISTIC [%s]: %s \n",QCoreApplication::applicationName().toStdString().c_str(), sender.toStdString().c_str(), message.toStdString().c_str());
        emit newLogEntry(STATISTIC_PRIORITY,message,sender);
    }
}

void Logger::logINFO(const QString &message, const QString &sender)
{
	QMutexLocker locker(&m_mutex);
    if(INFO_PRIORITY >= m_active_priority)
	{
		QTextStream out(&m_file);
		out << currentDateTimeString() << " [INFO] "<< " {"<<sender<<"} -- "<<message << "\n";
        fprintf(stderr,"{%s}:INFO [%s]: %s \n",QCoreApplication::applicationName().toStdString().c_str(), sender.toStdString().c_str(), message.toStdString().c_str());
		emit newLogEntry(INFO_PRIORITY,message,sender);
	}
}

void Logger::logWARNING(const QString &message, const QString &sender)
{
	QMutexLocker locker(&m_mutex);
    if(WARNING_PRIORITY >= m_active_priority)
	{
		QTextStream out(&m_file);
		out << currentDateTimeString() << " [WARNING] "<< " {"<<sender<<"} -- "<<message << "\n";
        fprintf(stderr,"{%s}:WARNING [%s]: %s \n",QCoreApplication::applicationName().toStdString().c_str(), sender.toStdString().c_str(), message.toStdString().c_str());
		emit newLogEntry(WARNING_PRIORITY,message,sender);
	}
}

void Logger::logCRITICAL(const QString &message, const QString &sender)
{
	QMutexLocker locker(&m_mutex);
    if(CRITICAL_PRIORITY >= m_active_priority)
	{
		QTextStream out(&m_file);
		out << currentDateTimeString() << " [CRITICAL] "<< " {"<<sender<<"} -- "<<message << "\n";
        fprintf(stderr,"{%s}:CRITICAL [%s]: %s \n",QCoreApplication::applicationName().toStdString().c_str(), sender.toStdString().c_str(), message.toStdString().c_str());
		emit newLogEntry(CRITICAL_PRIORITY,message,sender);
	}
}

void Logger::logERROR(const QString &message, const QString &sender)
{
	QMutexLocker locker(&m_mutex);
    if(ERROR_PRIORITY >= m_active_priority)
	{
		QTextStream out(&m_file);
		out << currentDateTimeString() << " [ERROR] "<< " {"<<sender<<"} -- "<<message << "\n";
        fprintf(stderr,"{%s}:ERROR [%s]: %s \n",QCoreApplication::applicationName().toStdString().c_str(), sender.toStdString().c_str(), message.toStdString().c_str());
		emit newLogEntry(ERROR_PRIORITY,message,sender);
	}
}

//PRIVATE SECTION -------------------
QString Logger::currentDateTimeString()
{
	QDateTime now = QDateTime::currentDateTime();
	return now.toString("dd.MM.yyyy-hh:mm:ss.zzz");
}

void loggerMessageOutput(QtMsgType type, const QMessageLogContext &context, const QString &msg)
{
    Q_UNUSED(context)
    //TODO USE CONTEXT FOR BETTER LOG INFO
	switch (type) 
	{
		case QtDebugMsg:
            LOG_DEBUG(msg,"System");
			break;
		case QtWarningMsg:
            LOG_WARNING(msg,"System");
			break;
		case QtCriticalMsg:
            LOG_CRITICAL(msg,"System");
			break;
		case QtFatalMsg:
            LOG_ERROR(msg,"System");
			abort();
        default:
            LOG_INFO(msg,"System");
        break;
	}
}

QString Logger::priorityToString(int priority)
{
    switch(priority)
    {
    case DISABLE_PRIORITY:
        return "DISABLE";
    case DEBUG_PRIORITY:
        return "DEBUG";
    case STATISTIC_PRIORITY:
        return "STATISTIC";
    case INFO_PRIORITY:
        return "INFO";
    case WARNING_PRIORITY:
        return "WARNING";
    case CRITICAL_PRIORITY:
        return "CRITICAL";
    case ERROR_PRIORITY:
        return "ERROR";
    }

    return "UNKNOWN";
}


