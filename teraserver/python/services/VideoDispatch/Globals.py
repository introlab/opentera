from services.VideoDispatch.ConfigManager import ConfigManager

redis_client = None
api_user_token_key = None
api_participant_token_key = None

UserTokenCookieName = 'VideoDispatchToken'
ParticipantTokenCookieName = 'VideoDispatchTokenParticipant'


config_man = ConfigManager()

# Global modules
# TODO can we do better ?
Flask_module = None
Twisted_module = None
WebRTC_module = None
OnlineUsers_module = None
