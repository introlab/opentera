from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.services.ServiceAccessManager import ServiceAccessManager
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

        if 'asset_uuids' not in access:
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

        if 'asset_uuids' not in access:
            return []

        return access['asset_uuids']

