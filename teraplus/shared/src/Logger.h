#ifndef LOGGER_H_
#define LOGGER_H_

#include "SharedLib.h"
#include <QObject>
#include <QFile>
#include <QDateTime>
#include <QMutex>



///Function used for redirection of Qt messages.
void loggerMessageOutput(QtMsgType type, const QMessageLogContext &context, const QString &msg);

/**
 This is a simple logger that is thread safe and is designed to be
 used as a single instance (singleton) and global for the whole application.
 Use the macros for writing to the log files easily.
 
 LOG_DEBUG(message,sender)
 LOG_STATISTIC(message,sender)
 LOG_INFO(message,sender)
 LOG_WARNING(message,sender)
 LOG_CRITICAL(message,sender)
 LOG_ERROR(message,sender)
 
 \Author Dominic Létourneau
 \Date	26 Novembre 2008
 
 \Modifications history ------------------------
 \Pierre Lepage	-	19 January 2009	-	ADDED : LOG_DEBUG()
 \Pierre Lepage	-	19 January 2009	-	ADDED : ActivationPriority enum
 \Pierre Lepage	-	19 January 2009	-	ADDED : setLogPriorityLevel()
 \Pierre Lepage	-	19 January 2009	-	ADDED : LOG_PRIORITY_LEVEL macro
 \Pierre Lepage	-	19 January 2009	-	ADDED : LOG_DEBUG macro
 \Pierre Lepage	-	19 January 2009	-	ADDED : LOG_REDIRECTION_ACTIVATION macro
 \Pierre Lepage	-	19 January 2009	-	ADDED : setRedirectionActivation()
 \Pierre Lepage	-	19 January 2009	-	ADDED : loggerMessageOutput()

 \Pierre Lepage    - 12 March 2014 - ADDED : logSTATISTIC()
 
 */
class SHAREDLIB_EXPORT Logger : public QObject
{
    Q_OBJECT

public:

    /**
        Logging priorities in order from no priority to high priority.
    */
    typedef enum {DISABLE_PRIORITY,DEBUG_PRIORITY,STATISTIC_PRIORITY,INFO_PRIORITY,WARNING_PRIORITY,CRITICAL_PRIORITY,ERROR_PRIORITY} ActivationPriority;


	/**
		Singleton, creates a single instance of the logger.
		The first call to instance will create the log file
		specified in the path. This function is thread safe.
		\param path The path of the log file, this has effect only on first call to instance(...)
		\return Logger* The pointer on the single instance of Logger
	*/
	static Logger* instance(const QString &path = "Logfile.txt");

    /**
        Convert priority type (int) to string.
        \param priority \ref ActivationPriority
        \return The string name of the priority
    */
    static QString priorityToString(int priority);

	/**
		Destroys the instance of the logger.
		This function is thread safe.
	*/
	static void destroy();

	/*
		Destructor. Closes the log file.
	*/
	~Logger();

	/**
		Set if the logger must redirect debug msg into log file.
		\param bool state
		This function is thread safe.
	*/
	void setRedirectionActivation(bool state);

	/**
		Set the priority log.
		\param ActivationPriority priority lvl
		This function is thread safe.
	*/
	void setLogPriorityLevel(ActivationPriority priority);

	/**
		Log with DEBUG level.
		\param message The log message
		\param sended A string to identify the sender of the message
		This function is thread safe.
	*/
	void logDEBUG(const QString &message, const QString &sender);
    /**
        Log with STATISTIC level.
        \param message The log message
        \param sended A string to identify the sender of the message
        This function is thread safe.
    */
    void logSTATISTIC(const QString &message, const QString &sender);
	/**
		Log with INFO level.
		\param message The log message
		\param sended A string to identify the sender of the message
		This function is thread safe.
	*/
	void logINFO(const QString &message, const QString &sender);

	/**
	 Log with WARNING level.
	 \param message The log message
	 \param sended A string to identify the sender of the message
	 This function is thread safe.
	 */
	void logWARNING(const QString &message, const QString &sender);

	/**
	 Log with CRITICAL level.
	 \param message The log message
	 \param sended A string to identify the sender of the message
	 This function is thread safe.
	 */
	void logCRITICAL(const QString &message, const QString &sender);

	/**
	 Log with ERROR level.
	 \param message The log message
	 \param sended A string to identify the sender of the message
	 This function is thread safe.
	 */
	void logERROR(const QString &message, const QString &sender);
	
	///Returns the current data and time
	static QString currentDateTimeString();

	
signals:
	
	/**
		Signal sent when a new log is entered.
		\param type the type of message
		\param message the log message
		\param sender the sender of the message (source)
	*/
	void newLogEntry(int type, QString message, QString sender);
	

private:

	///Single static instance of the logger
	static Logger* m_instance;
	///Constructor is private so only instance() can access it
	Logger(const QString &path);
	///The file where to log
	QFile m_file;
	///Mutex for thread safety
	static QMutex m_mutex;
	///Msg Priority
	static ActivationPriority m_active_priority;

};
///Macro setLogPriorityLevel level
#define LOG_REDIRECTION_ACTIVATION(state)(Logger::instance()->setRedirectionActivation(state))
///Macro setLogPriorityLevel level
#define LOG_PRIORITY_LEVEL(priority)(Logger::instance()->setLogPriorityLevel(priority))
///Macro to log DEBUG level
#define LOG_DEBUG(message,sender)(Logger::instance()->logDEBUG(message,sender))
///Macro to log STATISTIC level
#define LOG_STATISTIC(message,sender)(Logger::instance()->logSTATISTIC(message,sender))
///Macro to log INFO level
#define LOG_INFO(message,sender)(Logger::instance()->logINFO(message,sender))
///Macro to log WARNING level
#define LOG_WARNING(message,sender)(Logger::instance()->logWARNING(message,sender))
///Macro to log CRITICAL level
#define LOG_CRITICAL(message,sender)(Logger::instance()->logCRITICAL(message,sender))
///Macro to log ERROR level
#define LOG_ERROR(message,sender)(Logger::instance()->logERROR(message,sender))



#endif
