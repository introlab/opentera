from services.FileTransferService.ConfigManager import ConfigManager
from services.FileTransferService.libfiletransferservice.db.DBManager import DBManager

# Configuration manager
config_man = ConfigManager()

# Database manager
db_man = DBManager()

# Redis client & keys
redis_client = None

# Service
service = None



