# Generate a new alembic script : 

* Tutorial : https://alembic.sqlalchemy.org/en/latest/tutorial.html

```bash
alembic revision -m "create account table"
```

## Changes for next version (Sept 5 2024)

### TeraServer
**Modified t_users table**
* Add column user_2fa_enabled (Boolean, default=False)
* Add column user_2fa_otp_enabled (Boolean, default=False)
* Add column user_2fa_email_enabled (Boolean, default=False)
* Add column user_2fa_otp_secret (String(32), nullable=True)
* Add column user_force_password_change (Boolean, default=False)

## Changes for next version (Feb 6 2023)

### TeraServer
**Modified tables / constraints**
* TeraSite.site_name unique constraint removed
* TeraSessionParticipants.id_session add ondelete='cascade'
* TeraUserUserGroup: id_user_group = Column(Integer, ForeignKey("t_users_groups.id_user_group", ondelete='cascade'), nullable=False)
* TeraSession: id_creator_service - change "cascade set null" to "cascade delete"

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