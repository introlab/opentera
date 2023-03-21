# Access Roles
OpenTera access to [REST API](API) is limited depending on the role the currently logged on usertype (user, participant, device, service) has for a specific service.

Since the core module of OpenTera (TeraServer) is basically a service by itself, it defines its own access levels based on projects and sites objects (see [database objects](Database-Structure) for more information on those objects). Thus, it adheres to the [service-role model](Services-Access).

As users, participants, devices and services only have access to their particular API, roles are not defined the same depending on the API.

The tables below use this legend:

 ![ True](images/on_.png) : Role has access to that feature
 
 ![False](images/off.png) : Role doesn't has access to that feature
  
 ![Limit](images/lim.png) : Role has limited access to this feature. Typically, in case of an update, only certain fields can be modified. 

***
## Users
 
 This table shows the various features that are available according the user groups access level, and for super admin access.
 
 ## Data access
| Data [1]                              | Super Admin              | Site Role: *Admin* [2]   | Site Role: *User* [3]    | Project Role: *Admin* [4]    | Project Role: *User* 
| :---                                  | :---:                    | :---:                    | :---:                    | :---:                        | :---:
| **Assets**: Create                    | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Assets**: Read                      | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Assets**: Update                    | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Assets**: Delete                    | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png)
| **Devices**: Create                   | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Devices**: Read                     | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Devices**: Update                   | ![ True](images/on_.png) | ![ True](images/on_.png) | ![Limit](images/lim.png) | ![Limit](images/lim.png)     | ![Limit](images/lim.png)
| **Devices**: Delete                   | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png) 
| **Participant Groups**: Create        | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png)
| **Participant Groups**: Read          | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Participant Groups**: Update        | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png)
| **Participant Groups**: Delete        | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png)
| **Participants**: Create              | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Participants**: Read                | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Participants**: Update              | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Participants**: Delete              | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png) 
| **Projects**: Create                  | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Projects**: Read                    | ![ True](images/on_.png) | ![ True](images/on_.png) | ![Limit](images/lim.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Projects**: Update                  | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png)
| **Projects**: Delete                  | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Services**: Create                  | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Services**: Read                    | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Services**: Update                  | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Services**: Delete                  | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Sessions**: Create                  | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sessions**: Read                    | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sessions**: Update                  | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sessions**: Delete                  | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png)
| **Sessions Types**: Create            | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/on_.png)     | ![ True](images/off.png)
| **Sessions Types**: Read              | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sessions Types**: Update            | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png)
| **Sessions Types**: Delete            | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![False](images/off.png)
| **Sessions Events**: Create           | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sessions Events**: Read             | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sessions Events**: Update           | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sessions Events**: Delete           | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sites**: Create                     | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Sites**: Read                       | ![ True](images/on_.png) | ![ True](images/on_.png) | ![Limit](images/lim.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Sites**: Update                     | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Sites**: Delete                     | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **System Services**                   | ![False](images/off.png) | ![False](images/off.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **System Service: Logger**: Read      | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Users**: Create                     | ![ True](images/on_.png) | ![ True](images/lim.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Users**: Read                       | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Users**: Update                     | ![ True](images/on_.png) | ![ True](images/lim.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **Users**: Delete                     | ![ True](images/on_.png) | ![ True](images/lim.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **User Groups**: Create               | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **User Groups**: Read                 | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **User Groups**: Update               | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)
| **User Groups**: Delete               | ![ True](images/on_.png) | ![ True](images/on_.png) | ![False](images/off.png) | ![False](images/off.png)     | ![False](images/off.png)

[1] All data are filtered according to the specific user group access. For exemple, if **Sites: Read** is done, only sites where the user have access with its usergroups are read.

[2] Super admins always have a **Site Role: Admin** on all sites in the system

[3] Any user group with a role in a project automatically have a **Site Role: User** access

[4] Any user group with a **Site Role: Admin** automatically have a **Project Role: Admin**

 ## Features
| Feature [1]                                   | Super Admin              | Site Role: *Admin* [2]   | Site Role: *User* [3]    | Project Role: *Admin* [4]    | Project Role: *User* 
| :---                                          | :---:                    | :---:                    | :---:                    | :---:                        | :---:
| **Data entry forms request**                  | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Device - Participant assignation**          | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Device - Project assignation**              | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/on_.png)     | ![ True](images/off.png)
| **Device - Site assignation**                 | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/on_.png)     | ![ True](images/off.png)
| **Login**                                     | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Logout**                                    | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Online users list**                         | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Online participants list**                  | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Manage project access**                     | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/on_.png)     | ![ True](images/off.png)
| **Manage services roles**                     | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/off.png)     | ![ True](images/off.png)
| **Manage site access**                        | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/off.png)     | ![ True](images/off.png)
| **Service configuration (self)**              | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Service configuration (others)**            | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/on_.png)     | ![ True](images/off.png)
| **Service - Project assignation**             | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/off.png)     | ![ True](images/off.png)
| **Session Type - Device Type assignation**    | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/off.png)     | ![ True](images/off.png)
| **Session Type - Project assignation**        | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/off.png) | ![ True](images/on_.png)     | ![ True](images/off.png)
| **Statistics module**                         | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)
| **Managing sessions start/stop/resume**       | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png) | ![ True](images/on_.png)     | ![ True](images/on_.png)

[1] All features are limited to data that the user can access. For example, if an user can't access a specific project, that user won't be able to use any feature on that project.

[2] Super admins always have a **Site Role: Admin** on all sites in the system

[3] Any user group with a role in a project automatically have a **Site Role: User** access

[4] Any user group with a **Site Role: Admin** automatically have a **Project Role: Admin**

***

## Participants 

Access roles for participants are quite simpler than the users access roles. A participant only has access to objects that are directly linked to them. For example, a participant can only query the devices and sessions that are associated to it.

No write access is provided as of now to those objects, while this will change in the future.

***

## Devices

A device only has access to objects that are directly linked to them. For example, a device can only query the participants associated to it or the sessions into which the device was involved.

Similarly, a device can only create data related to an object linked to it. For example, it can only create assets for a session into which it was involved.

***

## Services

Services don't have specific roles. As they likely require more access than a user, a participant or a device, they don't have any specific limitation based on roles on what they can do with their API.

Of course, not all objects are exposed with the service API, and [login and authentication mecanisms](Login-and-authentification) are still required to access that API to limit access to those features.