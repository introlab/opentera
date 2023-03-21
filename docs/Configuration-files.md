Each service, including the core module, [TeraServer](TeraServer-Service), has an associated config file.

The details of those files are presented in each of the service. 

For the core module, [TeraServer](TeraServer-Service), there are 2 configuration files: the main configuration file and the NGINX configuration files.

# Core module - Configuration file 
The development configuration file can be found [here](https://github.com/introlab/opentera/blob/main/teraserver/python/config/TeraServerConfig.ini). It is a JSON-formatted file, separated in different sections. The following describe the required sections, and the parameters in each of them.

## Server section
`name` - the server name. Only used for display purpose. On a [deployed server](Deployment), this should be the internal name of the server, not the DNS of it.

`hostname` - the hostname that the server will listen on. Unless deploying on multiple servers, this should be left to the localhost value (127.0.0.1)

`port` - the internal port that the server will listen to. The external port that the server will respond to is managed by NGINX itself. Unless a very specific configuration needs to be put in place, this should be changed from the default value (4040).

`ssl_path` - the path where the SSL certificates are stored on the server. Defaults to the "certificates" folder. Used when generating local certificates.

`debug_mode` - if set to true, the server will be more verbose, especially on SQL and REST API queries.

The other parameters still left in the config file are deprecated and will be removed soon, if not already.

## Database section
`db_type` - the type of database used. This parameter, while in this config file, is currently unused since only [PostgreSQL](https://www.postgresql.org/) database are used right now (except for [tests](Running-tests), which use a local [SqlLite](https://www.sqlite.org) database).

`name` - the name of the database used by the core module.

`url` - the URL of the database server. Typically, should be left to 127.0.0.1 unless running the database engine on a different server.

`port` - the port to connect to the database server. Default should be 5432 for PostgreSQL database.

`username` & `password` - the username and password used to connect to the database server. **Please ensure that the user has full access to the database**, as errors will occur. See [database structure](Database-Structure) for more information on how to create the initial database.

## Redis section
`hostname`- hostname (URL) hosting the [Redis](https://redis.io/) server. In a typical scenario, the Redis server will be running as localhost (127.0.0.1).

`port` - the port of the Redis server. Typically, this should be left to the default value of 6379.

`db` - index of the Redis database to use. Defaults to 0.

`username` & `password` - the username and password used to connect to the Redis server. Empty values mean that no username and password are required to connect to the server.

***

# NGINX configuration file

The NGINX configuration is split into 2 files: [nginx.conf](https://github.com/introlab/opentera/blob/main/teraserver/python/config/nginx.conf) and [opentera.conf](https://github.com/introlab/opentera/blob/main/teraserver/python/config/opentera.conf).

## nginx.conf
This contains the main NGINX server configuration. Usually, there is no need to change that config file. However, the following elements might be of interest in a specific [server deployment](Deployment).

`listen 40075 ssl` - by default, sets the external listening port to 40075 using SSL encryption. The port could be changed to anything, and the `ssl` keyword could be removed if no encryption is required (**not recommended**).

`ssl_certificate`, `ssl_certificate_key` and `ssl_client_certificate` - path to the various certificates required by SSL encryption. Could be changed to match your specific server configuration. By default, will use certificates in the "certificates" folder.

## opentera.conf
This config file is included by the main `nginx.conf` file and contains the routing rules for each of the services in the system.

**You will need to adjust that file by yourself if you change the default services ports and according to the service you run on your system**.

Each `location` subsection should be self-explanatory and easy to understand and adjust, if required.