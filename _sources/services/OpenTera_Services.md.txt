# OpenTera Services Structure
The core of OpenTera is based on (micro)-services. This allow for extensibility and freedom for the developers to create 
new features according to needs in a separate way. 

## General structure and definition
A service can be defined as a standalone software (which could be written using any framework / programming language) 
that provides features that goes beyond the scope of the [core services](services.rst) in OpenTera. Each service can manage 
its own database and API, and provides client implementations (or not).

Basic service architecture is described in the [architecture overview](../Architecture-Overview).
  
## Communication mechanisms
Services can communicate with each other using a specific [service API](teraserver/api/API), but also using 
[internal communication structure](../developers/Internal-services-communication-module).
  
## System services
Those services are internal services that are available in the core OpenTera. Those services provides common features to 
the system, and should not be disabled unless specific requirements call for (such as never providing file transfer 
capability to a server setup).
  
Currently, the system services are the following:
- [**FileTransfer Service**](FileTransfer-Service), used to manage the various files required to be stored on the system
as assets
- [**Logging Service**](Logging-Service), used for internal technical and access logging
- [**VideoRehab Service**](Videorehab-Service), used to provide synchronous video conferencing capabilities in a 
rehabilitation context.
  
### TeraServer service
The OpenTera main server (TeraServer) is considered to be a specific case of system service. It is the base service
and is mandatory in any deployed solution. 
  
Considering TeraServer as a service allows to properly manage [project and site access](Services-Access), and can be addressed
in communication mechanisms, if needed.
  
## Services configuration
Each service can have a specific configuration depending on the user, participant or device. This configuration is 
defined in the `TeraServiceConfig` database model on the OpenTera service. That configuration could allow to specify 
values such as specific devices to use or a specific UI configuration. Default configuration is specified in the 
`TeraService` database model on the OpenTera service.
  
The configuration is stored in a json schema that is specified and validated with the schema specified in the 
`TeraService` database model.
  
The typical configuration structure is the following:
```javascript
  { Globals: {
                // Put "default" config values here with format:
                {name: value}
             }
    Specifics: [
                    {
                        id: xxxx, // Specific id of that config, for example hardware ID
                        // Put "overriden" config values here for that config id
                    },
                    {
                        id: xxxx, // Specific id of that config, for example hardware ID
                        // Put "overriden" config values here for that config id
                    },
               ]
  }
```
The `Globals` section provides default values independent of specific configuration (such as client ids or specific 
hardware). The `Specifics` section provides override value tied to a specific system. The `id` used to identify the 
specific configuration is client-defined, and could refer to a PC unique identifier, for example. 
