from .TeraAsset import TeraAsset
from .TeraDevice import TeraDevice
from .TeraDeviceParticipant import TeraDeviceParticipant
from .TeraDeviceProject import TeraDeviceProject
from .TeraDeviceSubType import TeraDeviceSubType
from .TeraDeviceType import TeraDeviceType
from .TeraParticipant import TeraParticipant
from .TeraParticipantGroup import TeraParticipantGroup
from .TeraProject import TeraProject
from .TeraServerSettings import TeraServerSettings
from .TeraService import TeraService
from .TeraServiceAccess import TeraServiceAccess
from .TeraServiceConfig import TeraServiceConfig
from .TeraServiceConfigSpecific import TeraServiceConfigSpecific
from .TeraServiceProject import TeraServiceProject
from .TeraServiceRole import TeraServiceRole
from .TeraServiceSite import TeraServiceSite
from .TeraSession import TeraSession
from .TeraSessionDevices import TeraSessionDevices
from .TeraSessionEvent import TeraSessionEvent
from .TeraSessionParticipants import TeraSessionParticipants
from .TeraSessionType import TeraSessionType
from .TeraSessionTypeSite import TeraSessionTypeSite
from .TeraSessionTypeProject import TeraSessionTypeProject
from .TeraSessionUsers import TeraSessionUsers
from .TeraSite import TeraSite
from .TeraTest import TeraTest
from .TeraTestType import TeraTestType
from .TeraUser import TeraUser
from .TeraUserGroup import TeraUserGroup
from .TeraUserUserGroup import TeraUserUserGroup
from .TeraUserPreference import TeraUserPreference
from .TeraUserUserGroup import TeraUserUserGroup

"""
    A map containing the event name and class, useful for event filtering. 
    Insert only useful events here.
"""
EventNameClassMap = {
    TeraAsset.get_model_name(): TeraAsset,
    TeraDevice.get_model_name(): TeraDevice,
    TeraParticipant.get_model_name(): TeraParticipant,
    TeraParticipantGroup.get_model_name(): TeraParticipantGroup,
    TeraProject.get_model_name(): TeraProject,
    TeraSession.get_model_name(): TeraSession,
    TeraSessionType.get_model_name(): TeraSessionType,
    TeraSite.get_model_name(): TeraSite,
    TeraUser.get_model_name(): TeraUser,
    TeraUserGroup.get_model_name(): TeraUserGroup,
    TeraTestType.get_model_name(): TeraTestType,
    TeraTest.get_model_name(): TeraTest
}

# All exported symbols
__all__ = ['TeraAsset',
           'TeraDevice',
           'TeraDeviceParticipant',
           'TeraDeviceProject',
           'TeraDeviceSubType',
           'TeraDeviceType',
           'TeraParticipant',
           'TeraParticipantGroup',
           'TeraProject',
           'TeraServerSettings',
           'TeraService',
           'TeraServiceAccess',
           'TeraServiceConfig',
           'TeraServiceConfigSpecific',
           'TeraServiceProject',
           'TeraServiceRole',
           'TeraServiceSite',
           'TeraSession',
           'TeraSessionDevices',
           'TeraSessionEvent',
           'TeraSessionParticipants',
           'TeraSessionType',
           'TeraSessionTypeProject',
           'TeraSessionTypeSite',
           'TeraSessionUsers',
           'TeraSite',
           'TeraTest',
           'TeraTestType',
           'TeraTestTypeSite',
           'TeraTestTypeProject',
           'TeraUser',
           'TeraUserGroup',
           'TeraUserPreference',
           'TeraUserUserGroup',
           'EventNameClassMap'
           ]
