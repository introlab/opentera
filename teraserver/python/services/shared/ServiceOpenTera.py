import jwt
import redis
import time
from modules.RedisVars import RedisVars
from libtera.redis.RedisClient import RedisClient
from requests import get, post, Response


class ServiceOpenTera:

    def __init__(self, backend_hostname: str, backend_port: int, service_uuid: str, redis_client: RedisClient):
        self.backend_hostname = backend_hostname
        self.backend_port = backend_port
        self.service_uuid = service_uuid
        self.redis_client = redis_client

        # Create service token for future uses
        self.service_token = self.service_generate_token()

    def service_generate_token(self):
        # Use redis key to generate token
        # Creating token with service info
        # TODO ADD MORE FIELDS?
        payload = {
            'iat': int(time.time()),
            'service_uuid': self.service_uuid
        }

        return jwt.encode(payload, self.redis_client.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey),
                          algorithm='HS256').decode('utf-8')

    def post_to_opentera(self, api_url: str, json_data: dict) -> Response:
        # Synchronous call to OpenTera backend
        url = "http://" + self.backend_hostname + ':' + str(self.backend_port) + api_url
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        return post(url=url, verify=False, headers=request_headers, json=json_data)

    def get_from_opentera(self, api_url: str, params: dict) -> Response:
        # Synchronous call to OpenTera backend
        url = "http://" + self.backend_hostname + ':' + str(self.backend_port) + api_url
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        return get(url=url, verify=False, headers=request_headers, params=params)

