# Logging Service
The Logging service is one of the system service in the OpenTera platform. It acts as a central logger for the services and modules to record events.

## Main script
The Logging service can be launched by running the [LoggingService.py](https://github.com/introlab/opentera/blob/main/teraserver/python/services/LoggingService/LoggingService.py) script. As a system service, it is also launched automatically when running the [main OpenTera service](../services/teraserver/TeraServer-Service)

## Configuration
Configuration files for the Logging service is similar to the basic [configuration files](../Configuration-files). It however adds a specific section for that service.

### Logging configuration section
`level`: the log level that is needed to be recorded in the logs. Anything below that level will not be recorded. See [LogEvent](https://github.com/introlab/opentera_messages/blob/master/proto/LogEvent.proto) for the different log levels available.

## Default port and location
By default, the service will listen to port 4041 (non-ssl) and will be at the root of the web server url (/logs).

## Web URLs
**Doc page** - by default at https://127.0.0.1:400075/logs/doc. Will display the [REST API](teraserver/api/API) documentation and test system. Useful to test queries manually.

## REST API
The REST API is currently limited only to get queries for the logs. As of now, only super-admins can queries such logs.

## Web Frontend
Currently, no web front-end is available for that service

## RPC API
None. This service uses the [asynchronous communication system](../developers/Internal-services-communication-module).
