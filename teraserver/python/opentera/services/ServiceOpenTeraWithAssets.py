from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_service_client, \
    current_login_type, current_user_client, current_device_client, current_participant_client, LoginType
from opentera.services.ServiceConfigManager import ServiceConfigManager
from opentera.modules.BaseModule import ModuleNames, create_module_event_topic_from_name

import opentera.messages.python as messages
from google.protobuf.json_format import ParseError
from google.protobuf.message import DecodeError
from twisted.internet import defer

import jwt
from abc import ABC, abstractmethod


class ServiceOpenTeraWithAssets(ServiceOpenTera, ABC):

    def __init__(self, config_man: ServiceConfigManager, this_service_info):
        ServiceOpenTera.__init__(self, config_man, this_service_info)

    @staticmethod
    def has_access_to_asset(access_token: str, asset_uuid: str) -> bool:
        try:
            access = jwt.decode(access_token, ServiceAccessManager.api_service_token_key, algorithms='HS256')
        except jwt.PyJWTError:
            return False

        if 'asset_uuids' not in access or 'requester_uuid' not in access:
            return False

        requester_uuid = ServiceOpenTeraWithAssets.get_current_requester_uuid()
        if access['requester_uuid'] != requester_uuid:
            return False

        if asset_uuid not in access['asset_uuids']:
            return False

        return True

    @staticmethod
    def get_accessible_asset_uuids(access_token: str) -> list:
        try:
            access = jwt.decode(access_token, ServiceAccessManager.api_service_token_key, algorithms='HS256')
        except jwt.PyJWTError:
            return []

        if 'asset_uuids' not in access or 'requester_uuid' not in access:
            return []

        requester_uuid = ServiceOpenTeraWithAssets.get_current_requester_uuid()
        if access['requester_uuid'] != requester_uuid:
            return []

        return access['asset_uuids']

    @staticmethod
    def get_current_requester_uuid() -> str:
        if current_login_type == LoginType.USER_LOGIN:
            return current_user_client.user_uuid
        if current_login_type == LoginType.PARTICIPANT_LOGIN:
            return current_participant_client.participant_uuid
        if current_login_type == LoginType.DEVICE_LOGIN:
            return current_device_client.device_uuid
        if current_login_type == LoginType.SERVICE_LOGIN:
            return current_service_client.service_uuid

        return str()

    @defer.inlineCallbacks
    def register_to_events(self):
        print('Registering to events...')
        # Always register to assets events
        yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
            ModuleNames.DATABASE_MODULE_NAME, 'asset'), self.database_event_received)

        # Need to register to events (base class)
        super().register_to_events()

    def database_event_received(self, pattern, channel, message):
        # Process asset event
        try:
            tera_event = messages.TeraEvent()
            if isinstance(message, str):
                ret = tera_event.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = tera_event.ParseFromString(message)

            database_event = messages.DatabaseEvent()

            # Look for DatabaseEvent
            for any_msg in tera_event.events:
                if any_msg.Unpack(database_event):
                    self.handle_database_event(database_event)

        except DecodeError as decode_error:
            print('ServiceOpenTeraWithAssets - DecodeError ', pattern, channel, message, decode_error)
        except ParseError as parse_error:
            print('ServiceOpenTeraWithAssets - Failure in database_event_received', parse_error)

    def handle_database_event(self, event: messages.DatabaseEvent):
        if event.object_type == 'asset':
            self.asset_event_received(event)

    @abstractmethod
    def asset_event_received(self, event: messages.DatabaseEvent):
        pass
