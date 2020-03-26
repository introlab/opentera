from services.VideoDispatch.ConfigManager import ConfigManager
# from services.VideoDispatch.libvideodispatch.db.DBManager import DBManager


redis_client = None
api_user_token_key = None
api_participant_token_key = None

UserTokenCookieName = 'VideoDispatchToken'
ParticipantTokenCookieName = 'VideoDispatchTokenParticipant'
config_man = ConfigManager()

# Database manager
# db_man = DBManager()
