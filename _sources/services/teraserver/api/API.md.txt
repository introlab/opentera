# REST API
OpenTera REST API is served by a [Flask](https://flask.palletsprojects.com) web server.

## General structure
OpenTera REST API main purpose is to interact with the [database objects](../../../developers/Database-Structure), to control the server itself, query information and to do various actions related to the modules and system services.

Since OpenTera is based on a micro-service architecture, each service can expose (or not) their own REST API. Only the OpenTera API is described here, as various services might implement other scheme and features.

### On a need-to-know basis
Every return value coming from the API will be filtered and checked against the requester [access level](../OpenTera_AccessRoles). For example, a user querying for projects will only have projects that it can access, other projects being filtered out at the server level. This ensure that data cannot leak by making a general query.

Data API is also structured on a need-to-know basis, meaning that the requester has to make individual queries (or add the appropriate parameters to each query) to have the information it needs. There is no complete data dump API that would return everything needed by a client with a single query (which would also be very client specific, as no client implementation requires the exact same information).

### API levels
There is 4 API levels in OpenTera: user API, participant API, device API and service API. A separation of those API was done in order to better control what each of these base user types can access.

Each API request can require [authentication](../../../developers/Login-and-authentication), or can be fully opened, depending on the specific calls.

* **[`User API`](https://github.com/introlab/opentera/tree/main/teraserver/python/modules/FlaskModule/API/user)** controls all that the users can do with OpenTera. Since most of the operations are initiated by users, this is the largest API, as every [database objects](../../../developers/Database-Structure) is somehow accessible using this API. 

* **[`Participant API`](https://github.com/introlab/opentera/tree/main/teraserver/python/modules/FlaskModule/API/participant)** controls all that the participants can do to interact with OpenTera. For security reasons, the features available here are limited and only the required ones are exposed. 

* **[`Device API`](https://github.com/introlab/opentera/tree/main/teraserver/python/modules/FlaskModule/API/device)** controls all that the devices can do to interact with OpenTera. Similarly to the participant API, the features available here are limited, and such is the returned information.

* **[`Service API`](https://github.com/introlab/opentera/tree/main/teraserver/python/modules/FlaskModule/API/service)** is a API that is only accessible by services. As such, return values are less limited than using one of the other API, though only features useful to services are implemented in that API.

### Documentation
Since code changes with time and that static documentation (such as this one) usually struggles to follow-up, an approach based on [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/) and [Swagger](https://swagger.io/) was implemented.

As such, each API functions are automatically documented on the server's documentation page located at `/doc`. On a local server (such as the default configuration used for development), the documentation can then be accessed at the full url `https://127.0.0.1:40075/doc`. 

The documentation system is interactive and can be used to test queries. As of now, only HTTP basic authentication is supported in the system.

## Request basics
Requests to the server can easily be initiated using the correct endpoint. The base endpoint for the API is `/api`, followed by the API level required. For example, the `user` API can be accessed using the `/api/user` endpoint.

To access a specific function, the function name must be appended to the endpoint, followed by the parameters. For example, an user querying projects would use the `/api/user/projects` function.

### GET
GET request are probably the most varied in term of parameters. See the documentation of each of those functions for a full list of the parameters.

All return values of the GET API are JSON-formatted string, and may include lists, dictionaries and any combination of those.

Some common parameters are standardized and used between all the GET API:

* `id_*` referring to a specific id. The end part of the id is the name of that [database object](../../../developers/Database-Structure). For example, `id_site` would refer to a specific site.

* `list` indicating that the return value should only contains minimal information. What is minimal information depends on each function and objects, but usually, the minimal information is only what is needed to display the returned information in a list.

* `with_*` indicating that further information will be returned in the reply. When querying [database objects](../../../developers/Database-Structure), this usually corresponds to `joins` between the various objects. 

### POST
When posting data to update or create new information, some structural convention must be respected:

* Posted data should be in JSON format and in the `json` part of the request

* A list of dictionary is needed (even if posting a single value) for the POST functions to properly works. The dictionary should have a key corresponding to the [database object name](../../../developers/Database-Structure) needing update, followed by a dictionary of values to update. For example, if a project should be created, the following JSON could be used:

`['project': { id_project: 0, id_site: 1, project_name: 'Doc Project'}]`

* The `id_*` value needs to be set to `0` if creating a new data. Otherwise, it will need to be put to the correct value of the object being updated

* Names of the keys in the object dictionary, if that object is a [database object](../../../developers/Database-Structure), should be properties of the model. Thus, it is easy to find what values can be posted by looking at the definition of each objects (or the documentation of the specific API).

### DELETE
Delete queries are standardized, taking only an `id` parameter, corresponding to the id of the object to delete. There is no need to specify the specific id name related to the object needed to be deleted.

## Further explanation on some of the API functions
Some API functions have a specific purpose that goes beyond the scope of the standard definition, and are described below.

* `/api/device/register` allows a device to register itself into OpenTera. The device can request a certificate from the server if the content-type of the request is set to `application/octet-stream`. Otherwise, a device token will be generated and returned to the device. In any case, the device won't be able to log in and access the device API before a user enables the device and assign it to at least one project. This function is also rate limited (currently to 10 requests per minute) to prevent mass creation of devices.

* `*/refresh_token` allows to get a dynamic token using a previous dynamic token, if such [authentication scheme](../../../developers/Login-and-authentication) is used and available for that API.

* `*/login` and `*/logout` allow the login and logout process to occurs. See [login and authentication](../../../developers/Login-and-authentication) for more information.

* `/api/user/forms` allows to query a [form structure](../../../developers/Form-Structure) corresponding to the specified object type.
