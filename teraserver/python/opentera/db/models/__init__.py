from .TeraAsset import TeraAsset
from .TeraDevice import TeraDevice
# from .TeraDeviceData import TeraDeviceData
from .TeraDeviceParticipant import TeraDeviceParticipant
from .TeraDeviceProject import TeraDeviceProject
from .TeraDeviceSubType import TeraDeviceSubType
from .TeraParticipant import TeraParticipant
from .TeraParticipantGroup import TeraParticipantGroup
from .TeraProject import TeraProject
from .TeraServerSettings import TeraServerSettings
from .TeraService import TeraService
from .TeraServiceProject import TeraServiceProject
from .TeraServiceAccess import TeraServiceAccess
from .TeraServiceRole import TeraServiceRole
from .TeraServiceConfig import TeraServiceConfig
from .TeraServiceConfigSpecific import TeraServiceConfigSpecific
from .TeraSession import TeraSession
from .TeraSessionEvent import TeraSessionEvent
from .TeraSessionParticipants import TeraSessionParticipants
from .TeraSessionUsers import TeraSessionUsers
from .TeraSessionDevices import TeraSessionDevices
from .TeraSessionType import TeraSessionType
from .TeraSessionTypeProject import TeraSessionTypeProject
from .TeraSite import TeraSite
from .TeraTest import TeraTest
from .TeraTestType import TeraTestType
from .TeraUser import TeraUser
from .TeraUserGroup import TeraUserGroup
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
    TeraSite.get_model_name(): TeraSite,
    TeraUser.get_model_name(): TeraUser,
    TeraUserGroup.get_model_name(): TeraUserGroup
}

# All exported symbols
__all__ = ['TeraAsset',
           'TeraDevice',
           # 'TeraDeviceData',
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
           # 'TeraServiceSite',
           'TeraServiceRole',
           'TeraSession',
           'TeraSessionDevices',
           'TeraSessionEvent',
           'TeraSessionParticipants',
           'TeraSessionType',
           'TeraSessionTypeProject',
           'TeraSessionUsers',
           'TeraSite',
           'TeraTest',
           'TeraTestType',
           'TeraUser',
           'TeraUserGroup',
           'TeraUserPreference',
           'TeraUserUserGroup',
           'EventNameClassMap'
           ]
