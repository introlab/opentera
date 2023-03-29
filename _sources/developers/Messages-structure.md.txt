# Internal messages structure

[Communication between the various modules and service](Internal-services-communication-module) and 
[between the server and the clients](Websockets-communication) is based on standardized messages and events. All of the 
messages and events are serialized and defined with the 
[protocol buffers (probuf)](https://developers.google.com/protocol-buffers) mechanism.

Since clients could be implemented in any language and will need to reuse the messages structure, an external repository, 
[opentera-messages](https://github.com/introlab/opentera_messages), is used for that purpose.

## Message wrappers
Wrappers are used to encapsulate message in a standard way, providing common fields and header for each message.

### General message wrapper (TeraMessage)
All messages that are going out through the [websocket channels](Websockets-communication) to the clients are wrapped in
the [TeraMessage](https://github.com/introlab/opentera_messages/blob/main/proto/TeraMessage.proto) structure.

The wrapper is quite simple and only contains an `Any` field. Since protobuf's Any allows for type detection, this 
allows the client to identify the type of the content of the message without explicitly having to try to cast to any 
known type and see if it makes senses.

`TeraMessage` wrapper is currently not used for internal message communications, only for communications with clients 
over websockets.

### Event wrapper (TeraEvent)
All events going in and out of the OpenTera server are wrapped in a 
[TeraEvent](https://github.com/introlab/opentera_messages/blob/main/proto/TeraEvent.proto) structure. 

The `Header` part of the event is self-explanatory. The `topic` field is used as a way to identify the 
[internal communication system](Internal-services-communication-module) topic being used to send that event.

A single `TeraEvent` wrapper can contains multiple events, if needed.

Same as with `TeraMessage`, the `Any` field in that structure allows for easier type detection in the receiver.

### Module message wrapper (TeraModuleMessage)
Message that are addressed to one of the module are wrapped in a 
[TeraModuleMessage](https://github.com/introlab/opentera_messages/blob/main/proto/TeraModuleMessage.proto).

The `Header` part of the message is self-explanatory. `seq` is a unique sequence number, while `source` contains who is 
sending the message to the module, while the `dest` contains the specific module topic.

A single `TeraModuleMessage` can contain multiple messages, if needed.

Same as with `TeraMessage`, the `Any` field in that structure allows for easier type detection in the receiver.

## Specific events messages

### Users, participants and devices
Those events indicate a status change in users, participants or devices. The specific status are defined and described 
in each of the messages proto below.

#### [DeviceEvent](https://github.com/introlab/opentera_messages/blob/main/proto/DeviceEvent.proto)
Device event, describing a device state (online / offline, busy / not busy) or status change (such as battery level).

#### [ParticipantEvent](https://github.com/introlab/opentera_messages/blob/main/proto/ParticipantEvent.proto)
Participant event, describing a state change (online / offline, busy / not busy).

#### [UserEvent](https://github.com/introlab/opentera_messages/blob/main/proto/UserEvent.proto)
User event, describing a state change (online / offline, busy / not busy).

### Sessions
Those events are generated with session management services.

#### [JoinSessionEvent](https://github.com/introlab/opentera_messages/blob/main/proto/JoinSessionEvent.proto)
Event to invite a specific user, participant and/or device to join a session.

#### [JoinSessionReplyEvent](https://github.com/introlab/opentera_messages/blob/main/proto/JoinSessionReplyEvent.proto)
Event indicating that a specific user, participant or device replied to a `JoinSessionEvent`

#### [LeaveSessionEvent](https://github.com/introlab/opentera_messages/blob/main/proto/LeaveSessionEvent.proto)
Event indicating that a specific user, participant or device left the session. Also use to indicate to a user, 
participant or device that it needs to leave the session now.

#### [StopSessionEvent](https://github.com/introlab/opentera_messages/blob/main/proto/StopSessionEvent.proto)
Event indicating that a specific session was terminated.

### OpenTera modules & system services
Those events are generated or used to communicate with some of the modules and systems service in the OpenTera platform.

#### [DatabaseEvent](https://github.com/introlab/opentera_messages/blob/main/proto/DatabaseEvent.proto)
Event generated when a database change (update, delete, create) occurred. Also see the 
[database objects](Database-Structure) for the model names.

#### [LogEvent](https://github.com/introlab/opentera_messages/blob/main/proto/LogEvent.proto)
Event sent to the [logging service](../services/Logging-Service) to add a system log in the log archive.

#### [LoginEvent](https://github.com/introlab/opentera_messages/blob/main/proto/LoginEvent.proto)
Event sent to the [logging service](../services/Logging-Service) to add a login event (successful or not) in the log 
archive.

#### [RPCMessage](https://github.com/introlab/opentera_messages/blob/main/proto/RPCMessage.proto)
Event used to make [remote procedure calls (RPC)](Internal-services-communication-module) with another service.
