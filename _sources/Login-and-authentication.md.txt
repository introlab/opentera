In OpenTera, login and authentication are 2 separate concept.

* **Authentication** refers to the process of having sufficient credentials to access the [REST API](API). Multiple authentication schemes are supported (see below)

* **Login** refers to the process of calling the appropriate login API, gets the current (temporary) token for the authentication and, optionally, opens a [websocket connection](Websockets-communication) to receive [messages and events](Messages-structure).

***

## Authentication

Supported authentication depends on the [API level](API) that is accessed.

### User API
* **HTTP Basic Auth**: Using username and password authentication, the requester can be identified and allowed (or not) to access that API. Since basic auth is implemented, it is quite important to always use SSL to encrypt communications for security purpose when [deploying to a server](Deployment)

* **Token Bearer**: Using the HTTP `Authorization` header in a request, it is possible to use a token for authentication instead of the standard username-password authentication:
  * The `<type>` value must be set to `OpenTera` and the `<credentials>` must contain a valid token. 
  * User token can be obtained with a call to the `login` API (see below). **Currently, users can't log only using a token**. To get the initial token, an HTTP Basic Auth scheme must be used. 
  * User tokens are set to expire after 1 hour, and a new token can be obtained before expiration by calling the `refreshtoken` API.

### Participant API
* **HTTP Basic Auth**: Using username and password authentication, the requester can be identified and allowed (or not) to access that API. Since basic auth is implemented, it is quite important to always use SSL to encrypt communications for security purpose when [deploying to a server](Deployment). 
  * **For participants, that authentication scheme is optional**. If no username and password are defined or if the `participant_login_enabled` is set to `false` for a specific participant (see [database objects](Database-Structure), this scheme will not work.

* **Token Bearer**: Using the HTTP `Authorization` header in a request, it is possible to use a token for authentication instead of the standard username-password authentication:
  * The `<type>` value must be set to `OpenTera` and the `<credentials>` must contain a valid token. 
  * A permanent login token can be used to obtain a valid dynamic (temporary) token for further queries. This allows a participant to login without having a username-password scheme with some restrictions (see below). The permanent token for a participant is automatically generated if `participant_token_enabled` is set in the `TeraParticipant` [database object](Database-Structure)
    * If the initial `login` API call is done with the permanent token of a participant instead of a standard username-password scheme, the available API calls are quite limited.
    * In the case where the initial `login` scheme is done with the participant permanent token, a dynamic token is not generated and thus can't be used for further calls.
    * In the API functions, the `role` parameter is used to check the access level. If the required role is set to `full`, a dynamic token will be required and the permanent token will not work. If the required role is set to `limited`, the permanent token will work to access that API function. For example, `@participant_multi_auth.login_required(role='limited')` will allow the decorated function to be called with a permanent token.
  * Participants dynamic token can be obtained with a call to the `login` API (see below) with a username-password scheme.
  * Participants tokens are set to expire after 1 hour, and a new token can be obtained before expiration by calling the `refreshtoken` API.

### Device API
* **Token Bearer**: Using the HTTP `Authorization` header in a request, it is possible to use a token for authentication for devices:
  * The `<type>` value must be set to `OpenTera` and the `<credentials>` must contain a valid token. 
  * A device token is permanent: the device will use the same token for every request. It must be stored somewhere safe on the device. See [`TeraDevice`](Database-Structure)
  * Only an enabled device (`device_enabled` in the `TeraDevice` database object) will be able to authenticate.

* **Token request argument**: Instead of using the HTTP `Authorization` header, it is also possible to append the token to a request by using the `token` argument.

* **Certificates**: **TO BE DOCUMENTED SOON**

### Service API
* **Token Bearer**: Using the HTTP `Authorization` header in a request, it is possible to use a token for authentication for services:
  * The `<type>` value must be set to `OpenTera` and the `<credentials>` must contain a valid token. 
  * A service token is permanent: the service will use the same token for every request. See [`TeraService`](Database-Structure)
  * Only an service device (`service_enabled` in the `TeraService` database object) will be able to authenticate.

* **Token request argument**: Instead of using the HTTP `Authorization` header, it is also possible to append the token to a request by using the `token` argument.

* **Certificates**: **TO BE DOCUMENTED SOON**

***

## Login
Even if the replies can vary a little depending on the [API level](API) being accessed, the login process is similar in each case. The login process is needed to get the [websocket](Websockets-communication), basic information about the logged on object and to get a dynamic token, if required, depending on the API level (see above).

Depending on the authentication scheme and the application, the login process might be optional. Without logging in, as long as the authentication scheme is respected, all API calls can proceed.

**Important note**: A user, participant or device will not come online in regards to the [User Manager Module](UserManager-module) unless a [websocket connection](Websockets-communication) is established. This is by design and by the fact that the REST API, by definition, is a stateless and asynchronous system, and thus OpenTera doesn't have any way to know if a user, participant or device is still there at the other end.

The login process can be summarized as:
1. Make a request with the correct authentication scheme to the `login` [API](API)
2. If the object type is enabled (see [database objects](Database-Structure)) and if the login credentials are valid, a return value containing at least the `_name`, the `_uuid` and the `websocket_url` will be returned. See the [REST API](API) for the specific return values for each of the specific `login` functions
3. Optionally, the client may connect to the `websocket_url`. There is a 60 seconds window to establish the connection, otherwise it will be denied. That url can only be used once: once a client is connected, it will not be available for further connections.

While recommended, a call to the `logout` is optional. When logging out, clean-up and dynamic token disabling will occur. If a websocket connection has been established, it will not close automatically - the client will need to close that connection after or before the `logout` call.