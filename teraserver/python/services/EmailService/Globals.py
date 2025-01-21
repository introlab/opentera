from services.EmailService.ConfigManager import ConfigManager
from services.EmailService.libemailservice.db.DBManager import DBManager

# Configuration manager
config_man = ConfigManager()

# Database manager
db_man = DBManager()

service = None

# Redis client & keys
redis_client = None
api_user_token_key = None
api_device_token_key = None
api_device_static_token_key = None
api_participant_token_key = None
api_participant_static_token_key = None


