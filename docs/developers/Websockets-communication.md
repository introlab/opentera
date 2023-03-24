# Websockets communication

Websockets are used within OpenTera to send [messages and events](Messages-structure) from the server to the client.

While a websocket can be used as a bidirectional communication channel, the websocket is only used in a unidirectional channel from the server to the client in OpenTera.

All websocket communication is encrypted using SSL certificates.

## Websockets management
Internally, websockets are managed by the [Twisted engine](https://twistedmatrix.com/) and a protocol has been defined for user, participant and device websockets. This allows to manage differently the connections depending on the base object type.

An automatic ping mechanism ensures that data is transmitted over the websocket at each 10 seconds to detect inactive clients or badly closed connection. If no reply is received by this mechanism, the webconnect channel will be automatically closed.

## Establishing a websocket connection
The websocket url to connect to will depend on the [object type](Database-Structure). To get that url, a `login` query must be made to the correct [REST API](../services/teraserver/api/API). See [Login and authentication](Login-and-authentication) for more information on the login process.

The returned url will be valid for 60 seconds. If no connection is established within that time frame, the url will have to be requested again.

## Communication over the websocket
All data sent from the server to the client will be formatted in a [protocol buffers (protobuf)](https://developers.google.com/protocol-buffers) serialized data format. The dictionary of messages and events is documented [here](Messages-structure).

Internally, each websocket connection will subscribe to specific events using the [internal services communication module](Internal-services-communication-module). The list of those events is defined according to the type of websocket. As with all communication within OpenTera, information will be filtered to only transmit the data that the associated object to that websocket has [access](../services/teraserver/OpenTera_AccessRoles).

* **User websocket**: All database events, [user manager module](../services/teraserver/UserManager-module) events, session events, device events, participant events, user events, direct events. Filtering occurs in the [UserEventManager](https://github.com/introlab/opentera/blob/main/teraserver/python/modules/UserEventManager.py) class.
* **Participant websocket**: Device events, participants event (self only), session events, direct events. Filtering occurs in the [ParticipantEventManager](https://github.com/introlab/opentera/blob/main/teraserver/python/modules/ParticipantEventManager.py) class.
* **Device websocket**: Device events (self only), participants event, session events, direct events. Filtering occurs in the [DeviceEventManager](https://github.com/introlab/opentera/blob/main/teraserver/python/modules/DeviceEventManager.py) class.

Direct events are always enabled by default on each of the websocket type, allowing to directly send an event or a message to a connected client, if that client type and uuid is known. See [here](Internal-services-communication-module) for more information on how to use the publish system to communicate with a connected client directly.
