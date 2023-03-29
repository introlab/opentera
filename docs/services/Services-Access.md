# Services Access Roles
Each service can define its own roles that are not limited to "admin" or "user". Specific services roles are stored in
the OpenTera service in the `TeraServiceRole` database model.

Service can further refine those roles by optionally attaching them to a specific project or site.

## Access roles association
Access roles can be attached to either of the following: user group, device or participant group. This architecture
allows to adapt to various configurations, but adds more complexity to the use or implementation. The
`TeraServiceAccess` database model in the OpenTera service defines those relationship.

Specific uses case includes associating an user group as "Admin" of a videoconferencing service, for example, allowing
that user group to have additional access in that service.

### OpenTera projects and sites roles
OpenTera main server (TeraServer) uses that mechanism to define access to projects and sites. On the creation of a new
site or project, the server creates "admin" and "user" roles for the OpenTera service and the specific site or project.

## Services and projects association
Each service can be associated to projects. This association is defined in the `TeraServiceProject` database model in
the OpenTera service. This association allows to expose only some of the services in the system to a specific project,
limiting the options for services linked to Session Types and allowing to use a single server instead for various
projects that depends on different services.
