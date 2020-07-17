from services.LoggingService.ConfigManager import ConfigManager
from services.LoggingService.libloggingservice.db.DBManager import DBManager

# Configuration manager
config_man = ConfigManager()

# Database manager
db_man = DBManager()

# Redis client & keys
redis_client = None
api_user_token_key = None
api_device_token_key = None
api_device_static_token_key = None
api_participant_token_key = None
api_participant_static_token_key = None


