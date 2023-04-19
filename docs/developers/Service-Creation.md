# Creating a new service
Since the OpenTera [architecture](../Architecture-Overview) allows for stand-alone services, there is not imposed 
constraints on the technical choices behind the creation of new services.

## Service creation steps
To create a new service using OpenTera, the following general steps should be used:

1. Assign a local listening port for the service and adjust the 
[NGINX config file](https://github.com/introlab/opentera/blob/main/teraserver/python/config/opentera.conf) accordingly.
2. Create the basic service structure (using the [OpenTera PyPi package](https://pypi.org/project/opentera/) if 
developing in Python).
3. Develop the service backend and, optionally, the frontend

### NGINX configuration
If your service expose a public API / front end, you will need to modify the NGINX config file.

Basically, you will need to add a new endpoint url and the correct local listening port for your service in the NGINX 
config file.

Of course, if you are developing a local service that doesn't have public access (such as a service to process data 
without any user interaction), this step might not be required.

### Basic service structure
There is no imposed service structure, as long as the service uses the [service API](../services/teraserver/api/API) and
the [communication mechanisms](Internal-services-communication-module) to communicate and exchange data with the core 
[TeraServer service](../services/teraserver/teraserver.rst).

To ease the creation of new services, 
[examples](https://github.com/introlab/opentera/tree/main/teraserver/python/examples) can be found in the main OpenTera
project. Those examples can serve as a building block to create your own services.

Also, providing some basic authentication and applying the communication mechanisms can be facilitated by using the 
[OpenTera PyPi package](https://pypi.org/project/opentera/) which only needs to be imported in your Python project. 

### Service backend and frontend
A service can provide a backend (such as a REST API) and a frontend.

While there's many way to do so, services source files are usually structured in two folders: `Frontend`, which should 
contain the necessary files for the service frontend (whether it is based on a web framework such as Angular or React or
something else) and a `Backend` folder containing the required source files to process data and present a REST API
(based on Flask or something else) to the user.
