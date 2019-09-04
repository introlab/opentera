from libtera.db.Base import db, BaseModel
import string
from string import digits, ascii_lowercase, ascii_uppercase
import random
import uuid


class TeraServerSettings(db.Model, BaseModel):
    __tablename__ = 't_server_settings'
    id_server_settings = db.Column(db.Integer, db.Sequence('id_server_settings_sequence'), primary_key=True,
                                   autoincrement=True)
    server_settings_name = db.Column(db.String, nullable=False, unique=True)
    server_settings_value = db.Column(db.String, nullable=False, unique=False)

    # Constants
    ServerTokenKey = "TokenEncryptionKey"
    ServerUUID = "ServerUUID"

    @staticmethod
    def create_defaults():
        # Create defaults settings
        # Token Encryption Key
        token_symbols = digits + ascii_uppercase + ascii_lowercase
        token_key = ''.join(random.choice(token_symbols) for i in range(32))  # Key length = 32 chars
        TeraServerSettings.set_server_setting(TeraServerSettings.ServerTokenKey, token_key)

        # Unique server id
        server_uuid = str(uuid.uuid4())
        TeraServerSettings.set_server_setting(TeraServerSettings.ServerUUID, server_uuid)

    @staticmethod
    def get_server_setting_value(setting_name: string):
        current_setting = TeraServerSettings.get_server_setting(setting_name=setting_name)
        if current_setting:
            return current_setting.server_settings_value
        else:
            return None

    @staticmethod
    def get_server_setting(setting_name: string):
        return TeraServerSettings.query.filter_by(server_settings_name=setting_name).first()

    @staticmethod
    def set_server_setting(setting_name: string, setting_value: string):
        # Check if setting already exists
        current_setting = TeraServerSettings.get_server_setting(setting_name=setting_name)

        # Update setting if already exists
        if current_setting is not None:
            current_setting.server_settings_value = setting_value
            TeraServerSettings.update(current_setting.id_server_settings, current_setting)
        else:
            # Insert setting if not
            current_setting = TeraServerSettings()
            current_setting.id_server_settings = 0
            current_setting.server_settings_name = setting_name
            current_setting.server_settings_value = setting_value
            TeraServerSettings.insert(current_setting)
