The user manager module acts as a central registry for the various connected user types (users, participants, devices). It tracks their current status in the system and can be queried using the [RPC](Internal-services-communication-module) communication system.

## States and tracked information

* **Online** state indicates that the specific object type (user, participant, device) has an active [websocket connection](Websockets-communication). If the object hasn't established any persistent connection (when only using the [REST API](API) for example), it will **not appear online**. It monitors the [UserEvent, DeviceEvent and ParticipantEvent messages](Messages-structure) to update this state.

* **Busy** state indicated that the specific object type (user, participant, device) is currently in an active live session. It monitors the [JoinSessionEvent, StopSessionEvent, LeaveSessionEvent and JoinSessionReplyEvent](Messages-structure) to update this state.

* **Status** state provide additional information related to an object, such as battery level or specific position in an environment. This is currently implemented as a JSON formatted string, so that each object can provides various status states depending on their type and needs.

## RPC functions
The user manager module can be queried using RPC calls. The following functions are available:

* **`online_users`**: returns a list of `user_uuid` of each of the currently online users
* **`busy_users`**: returns a list of `user_uuid` of each of the currently busy users
* **`status_users`**: return a list of `user_uuid` associated with a dictionary with 2 keys: `online` (bool) indicating if the user is currently online or not and `busy` (bool) indicating if the user is currently busy or not

* **`online_participants`**: returns a list of `participant_uuid` of each of the currently online participants
* **`busy_participants`**: returns a list of `participant_uuid` of each of the currently busy participants
* **`status_participants`**: return a list of `participant_uuid` associated with a dictionary with 2 keys: `online` (bool) indicating if the participant is currently online or not and `busy` (bool) indicating if the participant is currently busy or not

* **`online_devices`**: returns a list of `device_uuid` of each of the currently online devices
* **`busy_devices`**: returns a list of `device_uuid` of each of the currently busy devices
* **`status_devices`**: return a list of `device_uuid` associated with a dictionary with 2 keys: `online` (bool) indicating if the device is currently online or not, `busy` (bool) indicating if the device is currently busy or not and `status` (str) a JSON formatted string containing the status of the device
* **`update_device_status`**: a function to update the status of the device. Inputs: `uuid` (str) - the `device_uuid` of the device to update status, `status` (str) - the JSON formatted string of the status of that device and `timestamp` (int) - the timestamp of this status update (or the time at which the status was updated)

Code definition of those functions can be found [here](https://github.com/introlab/opentera/blob/main/teraserver/python/modules/UserManagerModule/UserManagerModule.py#L34)
