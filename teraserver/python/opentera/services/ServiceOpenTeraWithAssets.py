from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_service_client, \
    current_login_type, current_user_client, current_device_client, current_participant_client, LoginType
from opentera.services.ServiceConfigManager import ServiceConfigManager

import jwt


class ServiceOpenTeraWithAssets(ServiceOpenTera):

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

