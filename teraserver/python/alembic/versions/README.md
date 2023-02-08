# Generate a new alembic script : 

* Tutorial : https://alembic.sqlalchemy.org/en/latest/tutorial.html

```bash
alembic revision -m "create account table"
```

## Changes for next version (Feb 6 2023)

### TeraServer
**Modified tables / constraints**
* TeraSite.site_name unique constraint removed
* TeraSessionParticipants.id_session add ondelete='cascade'
* id_user_group = Column(Integer, ForeignKey("t_users_groups.id_user_group", ondelete='cascade'), nullable=False)
* class TeraServiceAccess(BaseModel, SoftDeleteMixin, SoftInsertMixin):

**Add deleted_at datetime field (set to NULL) to :**
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
- TeraSessionTypeSite
- TeraSessionUsers
- TeraSite
- TeraTest
- TeraTestType
- TeraTestTypeProject
- TeraTestTypeSite
- TeraUser
- TeraUserGroup
- TeraUserUserGroup

### LoggingService
- New table LoginEntry (create_all)