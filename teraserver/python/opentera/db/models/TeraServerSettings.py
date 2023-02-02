from opentera.db.Base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
import string
from string import digits, ascii_lowercase, ascii_uppercase
import random
import uuid


class TeraServerSettings(BaseModel):
    __tablename__ = 't_server_settings'
    id_server_settings = Column(Integer, Sequence('id_server_settings_sequence'), primary_key=True, autoincrement=True)
    server_settings_name = Column(String, nullable=False, unique=True)
    server_settings_value = Column(String, nullable=False, unique=False)

    # Constants
    ServerDeviceTokenKey = "TokenEncryptionKey"
    ServerParticipantTokenKey = "ParticipantTokenEncryptionKey"
    ServerUUID = "ServerUUID"
    ServerVersions = "ServerVersions"

    @staticmethod
    def create_defaults(test=False):
        # Create defaults settings
        # Token Encryption Key
        TeraServerSettings.set_server_setting(TeraServerSettings.ServerDeviceTokenKey,
                                              TeraServerSettings.generate_token_key(32))

        TeraServerSettings.set_server_setting(TeraServerSettings.ServerParticipantTokenKey,
                                              TeraServerSettings.generate_token_key(32))

        # Unique server id
        server_uuid = str(uuid.uuid4())
        TeraServerSettings.set_server_setting(TeraServerSettings.ServerUUID, server_uuid)

    @staticmethod
    def generate_token_key(length: int) -> str:
        token_symbols = digits + ascii_uppercase + ascii_lowercase
        token_key = ''.join(random.choice(token_symbols) for i in range(length))  # Key length = 32 chars
        return token_key

    @staticmethod
    def get_server_setting_value(setting_name: string):
        current_setting = TeraServerSettings.get_server_setting(setting_name=setting_name)
        if current_setting:
            return current_setting.server_settings_value
        else:
            return None

    @staticmethod
    def get_server_setting(setting_name: string):
        return TeraServerSettings.query.filter_by(
            server_settings_name=setting_name).first()

    @staticmethod
    def set_server_setting(setting_name: string, setting_value: string):
        # Check if setting already exists
        current_setting = TeraServerSettings.get_server_setting(setting_name=setting_name)

        # Update setting if already exists
        if current_setting is not None:
            current_setting.server_settings_value = setting_value
        else:
            # Insert setting if not
            current_setting = TeraServerSettings()
            current_setting.id_server_settings = None
            current_setting.server_settings_name = setting_name
            current_setting.server_settings_value = setting_value
            TeraServerSettings.db().session.add(current_setting)
        # Store object
        current_setting.commit()
