# Constants
class RedisVars:
    RedisVar_UserTokenAPIKey = "UserTokenAPIKey"
    RedisVar_DeviceTokenAPIKey = "DeviceTokenAPIKey"
    RedisVar_DeviceStaticTokenAPIKey = "DeviceStaticTokenAPIKey"
    RedisVar_ParticipantTokenAPIKey = "ParticipantTokenAPIKey"
    RedisVar_ParticipantStaticTokenAPIKey = "ParticipantStaticTokenAPIKey"
    RedisVar_ServiceTokenAPIKey = "ServiceTokenAPIKey"
    RedisVar_ServicePrefixKey = "service."

    @classmethod
    def build_service_rpc_topic(cls, service_key) -> str:
        return cls.RedisVar_ServicePrefixKey + service_key + '.rpc'

    @classmethod
    def build_service_message_topic(cls, service_key) -> str:
        return cls.RedisVar_ServicePrefixKey + service_key + '.messages'
