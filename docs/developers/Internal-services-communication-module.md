# Inter-service communication

Internal communication between modules and services (system or external) is done using a [Redis](https://redis.io/) server and database.

## Basic features of the internal communication module
The internal communication module allows to exchange data between service and modules running in different process and, potentially, on a different server.

Two modes are supported by the current implementation: asynchronous communication where data will published and received by the different subscribers in a non-blocking way, and a synchronous communication scheme where a call to a function on a remote service / module will block until a reply is received (or a time-out occurs).

Implementation is done in the [RedisClient](https://github.com/introlab/opentera/blob/main/teraserver/python/opentera/redis/RedisClient.py) and [RedisClientRPC](https://github.com/introlab/opentera/blob/main/teraserver/python/opentera/redis/RedisRPCClient.py). An instance of those class should be instantiated by each service requiring the use of this module.

### Get / Set scheme (Asynchronous communication)
This scheme allows to set variables in the Redis system that could be read by the various services. Typically, a service will write a value and another one will read that value when needed.

Currently, no synchronization mechanism was implemented and only one service should write any variable values to prevent conflicts. If a more dynamic system is required, the publish / subscribe scheme should probably be used instead.

Static variables are defined in the [RedisVars](https://github.com/introlab/opentera/blob/main/teraserver/python/opentera/redis/RedisVars.py) class and are commented there.

While, in theory, any variables can be used and set using this scheme, it is recommended to define those variables in the [RedisVars](https://github.com/introlab/opentera/blob/main/teraserver/python/opentera/redis/RedisVars.py) file to ease the documentation and following of those variables.

As of now, dynamic variables names are used to authorize or not an incoming [websocket](Websockets-communication) connection. In that case, when a [login](Login-and-authentication) is requested, the current session id is stored in the Redis database and used to validate that the websocket is allowed to connect.

### Publish / Subscribe scheme (Asynchronous communication)
Using "topics", the internal services communication allows for a publish / subscribe scheme where a publisher (for example, a service or a module updating the online status of an user) will update a specific topic name and where a subscriber (for example, a service who wants to do something when an user gets offline) can receive an event when that specific topic value is changed.

#### Topic naming convention
While in theory any topic name could be used, a convention was defined for the OpenTera to help debug and trace what is happening in the system, and prevent duplicate topic names with the same purpose. Depending on the publisher, the topic name will always have that structure:

`module.<module_name>.messages` for published [messages](Messages-structure) originating from the module <module_name>

`module.<module_name>.events` for [events](Messages-structure) needed to be received by the module <module_name> (which could also be managed by any subscriber)


`service.<service_key>.messages` for published [messages](Messages-structure) originating from the service with the key <service_key>

`service.<service_key>.events` for [events](Messages-structure) needed to be received by the service with the key <service_key> (which could also be managed by any subscriber)


`websocket.user.<user_uuid>.events` for [events](Messages-structure) that need to be sent to the user <user_uuid> connected with a websocket (which could also be managed by any subscriber)

`websocket.device.<device_uuid>.events` for [events](Messages-structure) that need to be sent to the device <device_uuid> connected with a websocket (which could also be managed by any subscriber)

`websocket.participant.<participant_uuid>.events` for [events](Messages-structure) that need to be sent to the participant <participant_uuid> connected with a websocket (which could also be managed by any subscriber)

### Remote Procedure Call (RPC) (Synchronous communication)
A service or a module can expose some functions that may be called by other modules and services. By providing a synchronous communication scheme, a caller may block until the remote function has been properly completed and then manage the return values, if needed.

In the Redis database, the remote procedure calls will be handled by the topic:

`service.<service_key>.rpc` where <service_key> is the service key implementing the function needed to be called

#### Declaring a remotely callable procedure
Currently, there is no way for a service to explicitly declare the list of their callable functions. The main reason for this is that the service will only receive a Redis event from the publish / subscribe on the specified topic above, and will have to handle the value of that topic to reply to it and/or execute what's requested.

The received message for an RPC request in the topic will be a [RPCMessage](Messages-structure), which will be parsed by the receiving service. The procedure can then return any JSON formatted reply, which will be forwarded to the caller.

Each of the service having a callable procedure thus need to document somehow their exposed RPC API. For the [core service](../services/teraserver/TeraServer-Service) and the system services, the RPC API is documented in this wiki.

#### Calling a remote procedure (function)
Knowing a service available procedure, the call can simply be made by using [RedisClientRPC](https://github.com/introlab/opentera/blob/main/teraserver/python/opentera/redis/RedisRPCClient.py):

`call` (for a call to a module) or `call_service` (for a call to a service). The `function_name` argument will represent the name of the remote function to call, and the `args` will be an array of arguments to send to that function. Currently, only the following argument types are supported:

* bool
* float
* int
* str
* bytes

The return value for the `call` or `call_service` function will be the return value of the remote procedure. If that value is None, either the remote procedure returned a None value, or the call didn't get through (time-out, invalid function name).
