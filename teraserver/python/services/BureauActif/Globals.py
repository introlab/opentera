from services.BureauActif.ConfigManager import ConfigManager

redis_client = None
api_user_token_key = None

TokenCookieName = 'BureauActifToken'
config_man = ConfigManager()