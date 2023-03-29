# VideoRehab Service
The VideoRehab service is one of the system service in the OpenTera platform. Its role is to provide the required 
framework for video-based rehabilitation sessions. Based on [WebRTC](https://webrtc.org/), providing an adapted 
user-interface for such usage. Implementation uses [Node.js](https://nodejs.org) and 
[Open-EasyRTC](https://github.com/open-easyrtc/open-easyrtc).

When requested to launch a video rehab session, this service will spawn a `Node` process for each of the session, 
creating isolated sessions and ensuring that only the invitees can access that session.

## Main script
The VideoRehab service can be launched by running the 
[VideoRehabService.py](https://github.com/introlab/opentera/blob/main/teraserver/python/services/VideoRehabService/VideoRehabService.py) 
script. As a system service, it is also launched automatically when running the 
[main OpenTera service](teraserver/teraserver.rst)

## Configuration
Configuration file for the VideoRehab service is similar to the basic [configuration files](../Configuration-files). It 
however adds a specific section for that service, and removes the `Database` since no database is used in that service.

### WebRTC configuration section
The `WebRTC` section in the configuration file specifies the parameters required to launch the WebRTC framework.

* `hostname`: the **external** hostname that will be used to connect to the WebRTC signaling server (Open-EasyRTC). It 
is important to use the external url, since that hostname will be sent and used by the clients (browsers) to establish 
the WebRTC connection.

* `external_port`: the **external** port on which the WebRTC signaling server can be reached. In its default 
configuration, it is set to the same port as the [main OpenTera service](teraserver/teraserver.rst) (40075)

* `local_base_port`: the **internal** port on which the WebRTC signaling server will listen. This is the base port: each
new session will listen to a port number on the range `local_base_port` to `local_base_port + max_sessions`. Since the 
NGINX router will redirects the external connection to the appropriate internal port (see below), there is no need to
open those ports externally.

* `max_sessions`: the maximum number of parallel sessions. This is linked to the local port ranges that could be opened 
(see `local_base_port`), but can also be used to limit the load of a specific server.

* `working_directory`: the base directory for the signaling server

* `executable`: the executable to launch. Since we are using Node.js, the executable should be `node`, but since, in 
theory, another signaling server could be used or if the executable is different because of system configuration, this 
parameter is available in the configuration file.

* `script`: the parameters to pass to the executable. By default, it is 
[`script.js`](https://github.com/introlab/opentera/blob/main/teraserver/easyrtc/server.js), which is the base script 
used by this service. However, if a custom or another script is needed, this is the parameter to update!

## Service setup
As this service relies on Node.js and external scripts, it is required to setup the environment of that service before 
using it. See [server deployment](../Deployment) and the [developers](../developers/Developers.rst) sections for more 
information on how to properly setup that environment.

## Default port and location
By default, the service will listen to port 4070 (non-ssl) and will be at the `/rehab` path on the base server URL.

## Web URLs
As each session will spawn in a different process and listen on a different internal (local) port, the Web URLs for that
service are dynamic, which contribute to the overall [security](../Security) of the OpenTera platform.

The base service is located at the `/rehab` path, while each of the video rehab sessions are located at the `/webrtc` 
path.

To properly route an external URLs to the correct port, a NGINX rule was defined to include the local port in the URL 
and redirect it to the correct listening server. This takes the form of, for example, 
`https://127.0.0.1:40075/webrtc/8081/` which will redirect the request to the server listening on the internal port 8081.

## REST API
This service doesn't expose any REST API.

## Web Frontend
The web frontends are provided and managed by the Node.js express server. The base files are located 
[here](https://github.com/introlab/opentera/tree/main/teraserver/easyrtc/protected). Included javascript files and 
assets are located [here](https://github.com/introlab/opentera/tree/main/teraserver/easyrtc/static).

## RPC API
This service uses the [asynchronous communication system](../developers/Internal-services-communication-module), 
but also provides the following RPC API:

### `session_manage`
#### Description
This function controls a session by allowing to start, stop, add and remove participants from it.

#### Parameters
A `session_manage` JSON formatted input string (format: `session_manage {action: '', ... }`) with the following fields 
and structure:

* **`action`** (string): the action that the service is required to take. The following actions are currently available:
  * `start`: starts a new session
  * `stop`: stops an active session
  * `invite`: sends an invitation to users, participants or devices in session in progress
  * `remove`: removes a user, participant or device from a session in progress
  * `invite_reply`: manages a session invitation reply

* **`id_session`** (int): the ID of the session to which to apply the action. If using the `start` action, a value of 
`id_session=0` can be used to create a totally new session. Otherwise, the specified session will be used. **This is a required parameter for each action**.

* **`parameters`** (string): Optional field containing session parameters.

#### Specific fields for `start` action
* **`id_creator_user`** (int): the ID of the user that created that session. For now, only users can create a video 
rehab session, though this might change in the future. Required only when creating a new session (`id_session` == 0).
* **`id_session_type`** (int): the ID of the session type of that session. Required only when creating a new session 
(`id_session` == 0).
* **`session_participants`, `session_users`, `session_devices`** (list): the participants, users and devices UUID to 
invite to that session.

#### Specific fields for `invite` and `remove` action
* **`session_participants`, `session_users`, `session_devices`** (list): the participants, users and devices UUID to 
invite to that session or to remove from.

#### Specific fields for `invite_reply` action
* **`parameters`** (dict): a dictionary of parameters to send in the 
[JoinSessionReplyEvent](https://github.com/introlab/opentera_messages/blob/master/proto/JoinSessionReplyEvent.proto) message:
  * **`reply_code`**: the reply code (value)
  * **`reply_msg`**: a message to send with the reply. Optional.

#### Return value
The return value will be a dictionary with the following fields:
* **`status`** (string): the status of the action command:
  * **`error`**: an error occurred. See the field `error_text` for a description of the error.
  * **`started`**: the session was properly started. A `session` field contains a JSON formatted string of the session 
  (based on the [database model](../developers/Database-Structure)), with the following added fields:
    * **`session_url_users`, `session_url_participants`, `session_url_devices`**: the URLs used to connect to the 
    session for users, participants and devices.
  * **`stopped`**: the session was properly stopped. A `session` field contains a JSON formatted string of the session 
  (based on the [database model](../developers/Database-Structure)).
  * **`invited`**: the invitations for the session were properly sent. A `session` field contains a JSON formatted 
  string of the session (based on the [database model](../developers/Database-Structure)).
  * **`removed`**: the specified invitees were properly removed from the session. A `session` field contains a JSON 
  formatted string of the session (based on the [database model](../developers/Database-Structure)).
  * **`OK`**: the session invitation reply was properly managed. A `session` field contains a JSON formatted string of 
  the session (based on the [database model](../developers/Database-Structure)).
