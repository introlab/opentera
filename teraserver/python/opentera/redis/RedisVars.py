# Constants
class RedisVars:
    # Variable used to store the User token encryption key
    RedisVar_UserTokenAPIKey = "UserTokenAPIKey"

    # Variable used to store the dynamic device encryption key
    RedisVar_DeviceTokenAPIKey = "DeviceTokenAPIKey"

    # Variable used to store the static device encryption key (used for initial login)
    RedisVar_DeviceStaticTokenAPIKey = "DeviceStaticTokenAPIKey"

    # Variable used to store the dynamic participant encryption key
    RedisVar_ParticipantTokenAPIKey = "ParticipantTokenAPIKey"

    # Variable used to store the static participant encryption key (used for initial login)
    RedisVar_ParticipantStaticTokenAPIKey = "ParticipantStaticTokenAPIKey"

    # Variable used to store the service token encryption key
    RedisVar_ServiceTokenAPIKey = "ServiceTokenAPIKey"

    # Service prefix to append to get the service information associated with a specific service UUID.
    # For example, a "get" to "service.<uuid>" would get the ServiceInfo object for that service
    RedisVar_ServicePrefixKey = "service."

    # User login attempt counter prefix
    RedisVar_UserLoginAttemptKey = "UserLoginAttempts."

    # Participant login attempt counter prefix
    RedisVar_ParticipantLoginAttemptKey = "ParticipantLoginAttempts."

    @classmethod
    def build_service_rpc_topic(cls, service_key) -> str:
        return cls.RedisVar_ServicePrefixKey + service_key + '.rpc'

    @classmethod
    def build_service_message_topic(cls, service_key) -> str:
        return cls.RedisVar_ServicePrefixKey + service_key + '.messages'
