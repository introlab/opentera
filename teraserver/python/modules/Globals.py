
from flask_httpauth import HTTPBasicAuth
from libtera.db.DBManager import DBManager


auth = HTTPBasicAuth()

db_man = DBManager()


# Constants
class TeraServerConstants:

    RedisVar_UserTokenAPIKey = "UserTokenAPIKey"
    RedisVar_DeviceTokenAPIKey = "DeviceTokenAPIKey"
    RedisVar_ParticipantTokenAPIKey = "ParticipantTokenAPIKey"


