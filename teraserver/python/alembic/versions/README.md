# Generate a new alembic script : 

* Tutorial : https://alembic.sqlalchemy.org/en/latest/tutorial.html

```bash
alembic revision -m "create account table"
```

Changes for next version (Feb 6 2023) :
* TeraSite.site_name unique constraint removed
* TeraSessionParticipants.id_session add ondelete='cascade'
* 
* Add deleted_at datetime field to :
- TeraAsset
- TeraDevice
- TeraDeviceParticipant
- TeraDeviceProject
- TeraDeviceSite
- TeraParticipant
- TeraParticipantGroup
- TeraProject
- TeraService
- TeraServiceAccess
- TeraServiceConfig
- TeraServiceConfigSpecific
- TeraServiceProject
- TeraServiceRole
- TeraServiceSite
- TeraSession
- TeraSessionDevices
- TeraSessionsEvent
- TeraSessionParticipants
- TeraSessionType
- TeraSessionTypeProject
- TEraSessionTypeSite
- TeraSessionUsers
- TeraSite
- TeraTest
- TeraTestType
- TeraTestTypeProject
- TeraTestTypeSite
- TeraUser
- TeraUserGroup
- TeraUserPreference
- TeraUserUserGroup

