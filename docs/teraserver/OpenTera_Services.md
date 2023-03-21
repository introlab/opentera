  # OpenTera Services Structure
  
  ## General structure and definition
  To document.
  
  ## Communication mecanisms
  To document.
  
  ## System services
  Those services are internal services that are not meant to be exposed directly to the end-users. Those services are 
  critical to the system, and cannot be configured or accessed like the other services.
  
  Currently, the system services are the following:
  - **Logging Service**, used for internal technical and access logging
  - **FileTransfer Service**, used to manage the various files required to be stored on the system as assets
  
  ### TeraServer service
  The OpenTera main server (TeraServer) is considered to be a specific case of system service. It is the base service
  and is mandatory in any deployed solution. 
  
  Considering TeraServer as a service allows to properly manage project and site access (see below), and can be adressed
  in communication mecanisms, if needed. 
  
  ## Services Access roles
  Each service can define its own roles that are not limited to "admin" or "user". Specific services roles are stored in
  the OpenTera service in the `TeraServiceRole` database model.
  
  Service can further refine those roles by optionally attaching them to a specific project or site.
  
  ### Access roles association
  Access roles can be attached to either of the following: user group, device or participant group. This architecture 
  allows to adapt to various configurations, but adds more complexity to the use or implementation. The 
  `TeraServiceAccess` database model in the OpenTera service defines those relationship.
  
  Specific uses case includes associating an user group as "Admin" of a videoconferencing service, for example, allowing
  that user group to have additionnal access in that service.
  
  ### OpenTera projects and sites roles
  OpenTera main server (TeraServer) uses that mechanism to define access to projects and sites. On the creation of a new
  site or project, the server creates "admin" and "user" roles for the OpenTera service and the specific site or project
  .
  
  ## Services and projects association
  Each service can be associated to projects. This association is defined in the `TeraServiceProject` database model on 
  the OpenTera service. This association allows to expose only some of the services in the system to a specific project,
   limiting the options for services linked to Session Types and allowing to use a single server instead for various 
  projects that depends on different services.
  
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
                  {name: value, .... }
               },
      Specifics: [
                      {
                          id: xxxx, // Specific id of that config, for example hardware ID
                          // Put "overriden" config values here for that config id
                      },
                      {
                          id: xxxx, // Specific id of that config, for example hardware ID
                          // Put "overriden" config values here for that config id
                      }, ...
                 ]
    }
  ```
  The `Globals` section provides default values independant of specific configuration (such as client ids or specific 
  hardware). The `Specifics` section provides override value tied to a specific system. The `id` used to identify the 
  specific configuration is client-defined, and could refer to a PC unique identifier, for example. 