import jwt
import redis
import time
from modules.Globals import TeraServerConstants
from requests import get


def service_generate_token(redis_client: redis.Redis, service_info: dict):
    if 'ServiceUUID' in service_info:
        # Use redis key to generate token
        # Creating token with service info
        # TODO ADD MORE FIELDS?
        payload = {
            'iat': int(time.time()),
            'service_uuid': service_info['ServiceUUID']
        }

        return jwt.encode(payload, redis_client.get(TeraServerConstants.RedisVar_ServiceTokenAPIKey),
                          algorithm='HS256').decode('utf-8')

    return None
