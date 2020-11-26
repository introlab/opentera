from services.BureauActif.ConfigManager import ConfigManager
from services.BureauActif.libbureauactif.db.DBManager import DBManager


redis_client = None
api_user_token_key = None
api_device_token_key = None
api_device_static_token_key = None
api_participant_token_key = None
api_participant_static_token_key = None

TokenCookieName = 'BureauActifToken'
config_man = ConfigManager()

# Database manager
db_man = DBManager()

# Global service object
service = None

