from opentera.config.ConfigManager import ConfigManager
from opentera.logging.LoggingClient import LoggingClient
import redis
import jwt
from typing import Set, Any


class DisabledTokenStorage:
    """
    This class is used to store disabled tokens in redis.
    """
    def __init__(self, redis_key: str):
        self.redis_key = redis_key
        self.redis_client = None
        self.token_key = None
        self.logging_client = None

    def config(self, config: ConfigManager, token_key: str) -> None:
        self.token_key = token_key
        self.redis_client = redis.Redis(host=config.redis_config['hostname'],
                                        port=config.redis_config['port'],
                                        username=config.redis_config['username'],
                                        password=config.redis_config['password'],
                                        db=config.redis_config['db'])

        self.logging_client = LoggingClient(config=config.redis_config,
                                            client_name="DisabledTokenStorage-" + str(self.redis_key))

        # Remove all expired tokens
        self.remove_all_expired_tokens(self.token_key)

    def add_disabled_token(self, token) -> Any:
        # Add token to set
        return self.redis_client.sadd(self.redis_key, token)

    def get_disabled_tokens(self) -> Set[str]:
        # Get all elements from the set
        return self.redis_client.smembers(self.redis_key)

    def is_disabled_token(self, token) -> bool:
        # Check if token is in set
        if not token:
            return True
        return self.redis_client.sismember(self.redis_key, token)

    def clear_all_disabled_tokens(self) -> Any:
        # Clear set
        return self.redis_client.delete(self.redis_key)

    def remove_disabled_token(self, token) -> Any:
        # Remove token from set
        self.redis_client.srem(self.redis_key, token)

    def remove_all_expired_tokens(self, key) -> Set[str]:
        to_be_removed: set = set()
        for token in self.redis_client.smembers(self.redis_key):

            if token is None:
                continue

            if len(token) == 0:
                self.redis_client.srem(self.redis_key, token)
                continue

            try:
                token_dict = jwt.decode(token, key, algorithms='HS256')
                # Expired tokens will throw exception.
                # If we continue here, tokens have a valid expiration time.
                # We should stop looking for expired tokens since they are added chronologically
                break
            except jwt.exceptions.ExpiredSignatureError as e:
                # Remove expired token
                to_be_removed.add(token)
                self.redis_client.srem(self.redis_key, token)
            except jwt.exceptions.InvalidSignatureError as e:
                # Token was signed with a different key, remove it
                self.redis_client.srem(self.redis_key, token)
                self.logging_client.log_error('DisabledTokenStorage.remove_all_expired_tokens', str(e))
            except jwt.exceptions.PyJWTError as e:
                self.logging_client.log_error('DisabledTokenStorage.remove_all_expired_tokens', str(e))
                continue

        # Return removed tokens
        return to_be_removed
